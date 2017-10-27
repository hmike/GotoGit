import sublime, sublime_plugin
import os
import re

'''
	repo https://github.com/hmike/GotoGit

	REF: https://github.com/hardikj/GGU-SL/blob/master/ggu.py#L120
	REF2: https://github.com/paccator/GotoRecent
	DOC: http://docs.sublimetext.info/en/latest/extensibility/packages.html#sublime-package-packages
'''


def getLines(self):
	(rowStart, colStart) = self.view.rowcol(self.view.sel()[0].begin())
	(rowEnd, colEnd)     = self.view.rowcol(self.view.sel()[0].end())

	lines = (str) (rowStart + 1)

	if rowStart != rowEnd:
		#multiple selection
		lines += "-" + (str) (rowEnd + 1)

	return lines

def find_dir(path, folder):
	items = os.listdir(path)
	if folder in items and os.path.isdir(os.path.join(path, folder)):
		return path
	dirname = os.path.dirname(path)
	if dirname == path:
		return None
	return find_dir(dirname, folder)

def get_git_url(path):
	#find git path
	folder_name, file_name = os.path.split(path)
	git_path = find_dir(folder_name, '.git')

	if not git_path:
		sublime.error_message('Could not find .git directory.')
		print('Could not find .git directory.')
		return

	#read config file
	gitc_path = os.path.join(git_path, '.git', 'config')

	with open(gitc_path, "r") as git_config_file:
		config = git_config_file.read()

	#r1 = r'(?:remote\s\")(.*?)\"\]'
	#raliases = re.findall(r1,config)
	#raliases is the branch!
	
	#host = 'github.com'
	#r2 = r'url\s=\s(?:https://%s/|%s:|git://%s|git@%s:)(.*)/(.*?)(?:\.git)'%(host, host, host, host)
	#r2 = r'url\s=\s(?:https://\S+/|\S+:|git://\S+|git@\S+:)(.*)/(.*?)(?:\.git)'%(host, host, host, host)
	
	#print(config)

	#extract remote url from config file
	r2 = r'url\s=\s(\S+\.git)'
	git_remote_url = re.findall(r2,config)[0]

	#parse git remote url
	r2 = r"((git|ssh|http(s)?)|(git@[\w\.]+))(:(//)?)([\w\.@\:/\-~]+)(\.git)(/)?"
	git_urls = re.findall(r2, git_remote_url)[0]
	if git_urls is None:
		sublime.error_message("Could not match git url")
		return None

	#build git web url
	protocol = git_urls[0]
	host = git_urls[3]
	repo = git_urls[6]

	if (protocol != 'https' and protocol != 'http'):
		protocol = 'http'

	if (host):
		host = host.split('@', 1)[1] + '/'

	return protocol + '://' + host + repo

def get_branch(git_path):
	"""
	   get current branch of the required repo
	"""

	ref = open(os.path.join(git_path, '.git', 'HEAD'), "r").read().replace('ref: ', '')[:-1]
	branch = ref.replace('refs/heads/','')

	return branch

def get_remote_branch(git_path, folder_name):
	"""
		Get remote branches
	"""

	gitc_path = os.path.join(git_path, '.git', 'config')

	with open(gitc_path, "r") as git_config_file:
		config = git_config_file.read()

	
	config = ("https://github.com/hardikj/GGU-SL.git\n"
		"https://hmike@github.com/hmike/GotoGit.git")

	config = "https://github.com/hardikj/GGU-SL.git"
	config = "https://hmike@github.com/hmike/GotoGit.git"
	config = "git@github.com:hmike/GotoGit.git"

	r1 = r'(?:remote\s\")(.*?)\"\]'
	raliases = re.findall(r1,config)

	host = 'github.com'
	#r2 = r'url\s=\s(?:https://%s/|%s:|git://%s|git@%s:)(.*)/(.*?)(?:\.git)'%(host, host, host, host)
	#r2 = r'((git|ssh|http(s)?)|(git@[\w\.]+))(:(//)?)(([\w]+@)?)([\w\.@\:/\-~]+)(\.git)(/)?'%(host, host, host, host, host, host, host, host, host, host)
	#r2 = r"((git|ssh|http(s)?)|(git@[\w\.]+))(:(//)?)(([\w]+@)?)([\w\.@\:/\-~]+)(\.git)(/)?"
	r2 = r"((git|ssh|http(s)?)|(git@[\w\.]+))(:(//)?)([\w\.@\:/\-~]+)(\.git)(/)?"
	#remotes = re.finditer(r2, config)
	remotes = re.findall(r2,config)
	#print(config)
	#print(remotes,remotes[0][0],remotes[0][3], remotes[0][6])

	if remotes is None:
		self.error_message("No remotes found")
		return None

	protocol = remotes[0][0]
	host = remotes[0][3]
	repo = remotes[0][6]

	if (protocol != 'https' and protocol != 'http'):
		protocol = 'http'

	if (host):
		host = host.split('@', 1)[1] + '/'

	#return protocol + '://' + host + repo

	
	
	return  raliases, remotes

# Extends TextCommand so that run() receives a View to modify.
class GotoGitCommand(sublime_plugin.TextCommand):
	def run(self, view):

		'''
		print("===========================")
		import subprocess
		output = subprocess.check_output("dir", stderr=subprocess.STDOUT, shell=True)
		#with Popen(["ifconfig"], stdout=PIPE) as proc:
		#    log.write(proc.stdout.read())
		#output = subprocess.call(["ls"])
		print("===========================")
		print(output)
		return

		output = os.system("git status")
		print(output)
		return

		from subprocess import check_output
		output = check_output("git status", shell=True).decode()
		print(output)
		return
		'''

		# Generate file path and position
		"""
			Get BASE URI
		"""
		(row,col) = self.view.rowcol(self.view.sel()[0].begin())
		row = row + 1
		path = os.path.realpath(self.view.file_name()) 
		#path = path + "#L" + str(row)
		folder_name, file_name = os.path.split(path)
		#print(path, folder_name, file_name)

		"""
			Get BASE URI
		"""
		BASE_URI = "https://github.com/hmike/"
		BASE_URI = get_git_url(path)

		"""
			Get branch
		"""
		branch = '/blob/master'

		"""
			Generate relative path
		"""
		relativePath = "prode/blob/master/app/models/bet.rb"

		git_path = find_dir(folder_name, '.git')

		if not git_path:
			sublime.error_message('Could not find .git directory.')
			print('Could not find .git directory.')
			return

		newPath = folder_name[len(git_path):]

		relativePath = newPath + '/' + file_name
		relativePath = relativePath.replace("\\", "/")

		"""
			Add line path
		"""
		linePath = '#L' + getLines(self)

		"""
			Build url
		"""
		url = BASE_URI + branch + relativePath + linePath

		"""
			Copy to clipboard
		"""
		sublime.set_clipboard(url)
		print("\n" + url + "\n")

		#sublime.status_message('Copied %s to clipboard.' % URL)
		#print('Copied %s to clipboard.' % URL)

		return

		'''
		for region in self.view.sel():
			# Only interested in empty regions, otherwise they may span multiple
			# lines, which doesn't make sense for this command.
			if region.empty():
				# Expand the region to the full line it resides on, excluding the newline
				line = self.view.line(region)
				# Extract the string for the line, and add a newline
				lineContents = self.view.substr(line) + '\n'
				# Add the text at the beginning of the line
				#self.view.insert(line.begin(), lineContents)
				#self.view.insert(view, 0, lineContents)
				print(REPO_URL + '#L' + lineContents)
		'''