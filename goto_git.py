import sublime, sublime_plugin
import os
import re

def get_lines(self):
	(rowStart, colStart) = self.view.rowcol(self.view.sel()[0].begin())
	(rowEnd, colEnd)     = self.view.rowcol(self.view.sel()[0].end())

	lines = "L" + (str) (rowStart + 1)

	if rowStart != rowEnd:
		#multiple selection
		lines += "-L" + (str) (rowEnd + 1)

	return lines

def find_dir(path, folder):
	items = os.listdir(path)

	if folder in items and os.path.isdir(os.path.join(path, folder)):
		return path

	dirname = os.path.dirname(path)

	if dirname == path:
		return None

	return find_dir(dirname, folder)

def get_git_url(git_config_path):
	#read config file
	gitc_path = os.path.join(git_config_path, '.git', 'config')

	with open(gitc_path, "r") as git_config_file:
		config = git_config_file.read()

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

def get_branch(git_config_path):
	ref = open(os.path.join(git_config_path, '.git', 'HEAD'), "r").read().replace('ref: ', '')[:-1]
	branch = ref.replace('refs/heads/','')

	return branch

# Extends TextCommand so that run() receives a View to modify.
class GotoGitCommand(sublime_plugin.TextCommand):
	def run(self, view):
		"""
			Get current file/folder paths
		"""
		(row,col) = self.view.rowcol(self.view.sel()[0].begin())
		row = row + 1
		file_path = os.path.realpath(self.view.file_name()) 
		folder_name, file_name = os.path.split(file_path)
		

		"""
			Get git config path
		"""
		git_config_path = find_dir(folder_name, '.git')
		if not git_config_path:
			sublime.error_message('Could not find .git directory.')
			print('Could not find .git directory.')
			return

		"""
			Get git url
		"""
		git_url = get_git_url(git_config_path)

		"""
			Get branch
		"""
		branch = '/blob/' + get_branch(git_config_path)

		"""
			Generate relative path
		"""

		git_path = folder_name[len(git_config_path):]

		relative_path = git_path + '/' + file_name
		relative_path = relative_path.replace("\\", "/")

		"""
			Add line number
		"""
		line_path = '#' + get_lines(self)

		"""
			Build url
		"""
		URL = git_url + branch + relative_path + line_path

		"""
			Copy to clipboard
		"""
		sublime.set_clipboard(URL)
		sublime.status_message('Copied %s to clipboard.' % URL)
		print('Copied %s to clipboard.' % URL)

		return
