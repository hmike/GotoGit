import sublime, sublime_plugin
import os

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
	folder_name, file_name = os.path.split(path)
	git_path = find_dir(folder_name, '.git')

	if not git_path:
		sublime.error_message('Could not find .git directory.')
		print('Could not find .git directory.')
		return

	return git_path

def get_branch(git_path):
	"""
	   get current branch of the required repo
	"""

	ref = open(os.path.join(git_path, '.git', 'HEAD'), "r").read().replace('ref: ', '')[:-1]
	branch = ref.replace('refs/heads/','')

	return branch

# Extends TextCommand so that run() receives a View to modify.
class GotoGitCommand(sublime_plugin.TextCommand):
	def run(self, view):


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


		"""
			Generate relative path
		"""
		relativePath = "prode/blob/master/app/models/bet.rb"
		gitUrl = get_git_url(path)
		newPath = folder_name[len(gitUrl):]
		#print(folder_name, gitUrl, newPath)

		relativePath = newPath + file_name

		"""
			Add line path
		"""
		#print(getLines(self))
		linePath = '#L' + getLines(self)


		"""
			Build url
		"""
		url = BASE_URI + relativePath + linePath

		"""
			Copy to clipboard
		"""
		sublime.set_clipboard(url)
		print("\n" + url + "\n")

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