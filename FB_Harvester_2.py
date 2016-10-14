#!/usr/bin/env python2
'''
	Facebook Pages/Groups Crawler v0.5
	
Current version supports:


Bug Fixes:
- Multithreading
'''

__version__ = 0.5

try:
	import urllib2, json, os, sys, requests
except ImportError:
	print "[!] Error importing one or more libraries\n[~] Leaving...\n\n"
	exit(-1)

#Defining core functions and data structures
def HTTP_Link(URI):
	url_conn = urllib2.urlopen(URI)
	raw_conn_data = url_conn.read()
	json_data = json.loads(raw_conn_data)
	return json_data

fields = {
		"Post_Fields"    : "id,application,caption,created_time,description,from,link,message,message_tags,name,object_id,picture,place,privacy,properties,shares,source,to,type,updated_time",
		"Comment_Fields" : "id,attachment,comment_count,created_time,from,like_count,message,message_tags,object,parent"
		 }


'''
 Write_Object_Likes(Object_Data, File_Desc)
 Object_Data => Likes JSON data
 File_Desc   => File Descriptor pointing at the Likes file to be created
'''

def Write_Object_Likes(Object_Data, File_Desc):

	while True:
		json.dump( Object_Data['data'], File_Desc )
		
		if 'paging' in Object_Data:
			if 'next' in Object_Data['paging']:
				Object_Data = HTTP_Link(Object_Data['paging']['next'])
			else:
				break
		else:
			break


#Defining parsing functions
def Parse_Posts_IDs(Object_ID, App_ID, App_Sec, Number_of_Posts = 0, Object_Type = None):
	if Object_Type == 'page':
		request_url = "https://graph.facebook.com/v2.7/%s/posts?key=value&access_token=%s|%s&fields=id&limit=%s" % (Object_ID, App_ID, App_Sec, str(Number_of_Posts))
	elif Object_Type == 'group':
		request_url = "https://graph.facebook.com/v2.7/%s/feed?key=value&access_token=%s|%s&fields=id&limit=%s" % (Object_ID, App_ID, App_Sec, str(Number_of_Posts))
	else:
		print "[!] Error Object Type!\n\n"
		exit(-1)
	
	try:
		json_data = HTTP_Link(request_url)
	except:
		print "[!] Error Parsing Posts\n\n"
		exit(-1)
	return json_data

def Parse_Post_Info(Post_ID, App_ID, App_Sec):
	request_url = "https://graph.facebook.com/v2.7/%s/?key=value&access_token=%s|%s&fields=%s" % (Post_ID, App_ID, App_Sec,fields['Post_Fields'])
	try:
		json_data = HTTP_Link(request_url)
	except:
		print "[!] Error Parsing Post Information\n\n"
		exit(-1)
	return json_data

def Parse_Comments_IDs(Object_ID, App_ID, App_Sec):
	request_url = "https://graph.facebook.com/v2.7/%s/comments?key=value&access_token=%s|%s&fields=id" % (Object_ID, App_ID, App_Sec)
	try:
		json_data = HTTP_Link(request_url)
	except:
		print "[!] Error Parsing Comments\n\n"
		exit(-1)
	return json_data

def Parse_Comment_Info(Object_ID, App_ID, App_Sec):
	request_url = "https://graph.facebook.com/v2.7/%s/?key=value&access_token=%s|%s&fields=%s" % (Object_ID, App_ID, App_Sec, fields['Comment_Fields'])
	try:
		json_data = HTTP_Link(request_url)
	except:
		print "[!] Error Parsing Comment Info\n\n"
		exit(-1)
	return json_data

def Parse_Object_Likes(Object_ID, App_ID, App_Sec):
	request_url = "https://graph.facebook.com/v2.7/%s/likes?key=value&access_token=%s|%s" % (Object_ID, App_ID, App_Sec)
	try:
		json_data = HTTP_Link(request_url)
	except:
		print "[!] Error Parsing Likes\n\n"
		exit(-1)
	return json_data


# Not possible to parse post's shares with an app access token. A user access token is needed.

def Parse_Post_Comments(Post_ID, App_ID, App_Sec, Number_of_Comments = 0):
	request_url = "https://graph.facebook.com/v2.7/%s/comments?key=value&summary=true&access_token=%s|%s&fields=%s&limit=%s" % (Post_ID, App_ID, App_Sec, fields['Comment_Fields'], str(Number_of_Comments))
	try:
		json_data = HTTP_Link(request_url)
	except:
		print "[!] Error Parsing Post Comments\n"
		exit(-1)
	return json_data

def Parse_Post_Likes(Post_ID, App_ID, App_Sec):
	request_url = "https://graph.facebook.com/v2.7/%s/likes?key=value&summary=true&access_token=%s|%s" % (Post_ID, App_ID, App_Sec)
	try:
		json_data = HTTP_Link(request_url)
	except:
		print "[!] Error Parsing Post Likes\n"
		exit(-1)
	return json_data


def Dump_Post_Data(my_post_id, myapp_id, myapp_sec, current_path):

	# Creating post's folder
	post_id_dir = current_path + my_post_id
	os.makedirs(post_id_dir)
	post_id_dir = post_id_dir + '/'
	
	# Creating post's .Info file
	fp = open(post_id_dir+my_post_id+'.Info','w')
	
	# Getting post's likes and comments count, and adding them to our main post's information json structure
	mydat = Parse_Post_Info(my_post_id, myapp_id, myapp_sec)
	mydat['likes_count'] = str(Parse_Post_Likes(my_post_id, myapp_id, myapp_sec)['summary']['total_count'])
	mydat['comments_count'] = str(Parse_Post_Comments(my_post_id, myapp_id, myapp_sec)['summary']['total_count'])
	
	# Writing post's data into .Info file
	json.dump(mydat, fp)
	fp.close()
	
	# Creating post's .Likes file
	fp = open(post_id_dir+my_post_id+'.Likes','w')
	
	# Writing post's likes list into .Likes file
	Write_Object_Likes(Parse_Object_Likes(my_post_id, myapp_id, myapp_sec), fp)
	fp.close()
	
	# Creating post's .Comments directory
	os.makedirs(post_id_dir+my_post_id+'.Comments')
	
	# Parsing post's comments by ID's only
	comm_dat = Parse_Comments_IDs(my_post_id, myapp_id, myapp_sec)
	
	# Preparing our hierarchy
	post_id_dir = post_id_dir + my_post_id + '.Comments/'

	while True:
		for i in comm_dat['data']:
			
			# Getting comment's information
			comm_info = Parse_Comment_Info(i['id'], myapp_id, myapp_sec)
			
			# Creating a directory for every comment
			os.makedirs(post_id_dir+i['id'])
			comm_dir = post_id_dir + i['id'] + '/'
			
			# Creating comment's .Info file
			fp = open(comm_dir+i['id']+'.Info','w')
			
			# Writing comment's information into .Info file
			json.dump( comm_info, fp )
			fp.close()
			
			# Creating comment's .Likes file
			fp = open(comm_dir+i['id']+'.Likes','w')
			
			# Writing comment's likes list
			Write_Object_Likes(Parse_Object_Likes(i['id'], myapp_id, myapp_sec) ,fp)
			fp.close()
			
			if ('comment_count' in comm_info) and ( comm_info['comment_count'] != '0'):
									
				# Creating comment's .Replies directory
				comm_dir = comm_dir + i['id'] + '.Replies'
				os.makedirs(comm_dir)
				comm_dir = comm_dir + '/'
				
				# Parsing comment's replies by ID's only
				replies_dat = Parse_Comments_IDs(i['id'], myapp_id, myapp_sec)
				
				for rep_id in replies_dat['data']:
					
					# Getting reply's information
					reply_info = Parse_Comment_Info(rep_id['id'], myapp_id, myapp_sec)
					
					# Create a directory for each reply
					reply_dir = comm_dir + rep_id['id']
					os.makedirs(reply_dir)
					reply_dir = reply_dir + '/'
					
					# Creating reply's .Info file
					fp = open(reply_dir + rep_id['id'] + '.Info', 'w')
					
					# Writing reply's information into .Info file
					json.dump(reply_info, fp)
					fp.close()
					
					# Creating reply's .Likes file
					fp = open(reply_dir + rep_id['id'] + '.Likes', 'w')
					
					# Writing reply's likes list
					Write_Object_Likes(Parse_Object_Likes(rep_id['id'], myapp_id, myapp_sec), fp)
					fp.close()
			
		break
		
	print "[~] Done Post!"

def Get_ID_By_URI(URI, URI_Type = None):
	try:
		req = requests.get(URI)
	except:
		print "[!] Cannot Connect to the provided URI\n\n"
		exit(-1)
	
	if URI_Type == 'group':
		str_offset = req.text.find('group_id')
		prefix_offset = req.text[ str_offset : str_offset+40 ].find(',')
		Object_ID = req.text[ str_offset+10 : str_offset + prefix_offset ]
	elif URI_Type == 'page':
		str_offset = req.text.find('page_id')
		prefix_offset = req.text[str_offset : str_offset+40].find('&')
		Object_ID = req.text[ str_offset+8 : str_offset + prefix_offset]
		
	 
	return Object_ID

def Get_Name_By_ID(Object_ID, App_ID, App_Sec):
	request_url = "https://graph.facebook.com/v2.7/%s/?key=value&access_token=%s|%s" % (Object_ID, App_ID, App_Sec)
	try:
		json_data = HTTP_Link(request_url)
	except:
		print "[!] Error getting group's name\n\n"
		exit(-1)
		
	return json_data['name'].replace(' ','.')
	


if __name__ == "__main__":
	
	# Preparing main crawling parameters
	App_Acc_ID  = ""			# Application Access ID
	App_Acc_SEC = ""			# Application Access Secret Key
	
	print "[~] Do you want to crawl a group or a page?\n[~] Please Answer with either group or page\n[~] Example input: group\n[~] Answer:",
	input_object_type = raw_input()
	
	while input_object_type != 'group' and input_object_type != 'page':
		print "[~] Invalid answer, please only answer with either group or page\n[~] Answer:",
		input_object_type = raw_input()
	
	print "\n\n[~] Do you know your " + input_object_type + " ID?\n[~] Please answer by either yes or no\n[~] Example input: yes\n[~] Answer:",
	ID_Known = raw_input()
	if ID_Known == 'yes':
		print "\n\n[~] Please enter your " + input_object_type + " ID\n[~] Answer:",
		input_object_id = raw_input()
	else:
		print "\n\n[~] Please enter your " + input_object_type + " URL\n[~] Answer:",
		input_object_url = raw_input()
		print "[~] Please wait until getting the ID ...\n"
		input_object_id = Get_ID_By_URI(input_object_url, URI_Type = input_object_type)
		print "[~] " + input_object_type + " ID is " + input_object_id
	
	print "\n\n[~] Please specify the number of posts you want to crawl\n[~] Answer:",
	input_posts_num = raw_input()
	
		
	# Preparing directory hierarchy
	dir_name = 'Groups' if input_object_type == 'group' else 'Pages'
	Object_Name = Get_Name_By_ID(input_object_id, App_Acc_ID, App_Acc_SEC) 
	full_path = './Results/' + dir_name + '/' + Object_Name
	
	# Creating page's
	try:
		os.makedirs(full_path)
	except:
		print "[!] Cannot create folder hierarchy\n\n"
		exit(-1)
	
	full_path = full_path + '/'
	# Example public group, Raspberry Pi Group ID = "242826222478973"
	
	mydat = Parse_Posts_IDs(input_object_id, App_Acc_ID, App_Acc_SEC, Number_of_Posts = int(input_posts_num,10), Object_Type = input_object_type)
	
	for i in mydat['data']:
		#print i['id']
		Dump_Post_Data(i['id'], App_Acc_ID, App_Acc_SEC, full_path)
