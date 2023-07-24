import re
import sys
import os
import struct
from common import *

class ParseVar():
	contentIndex = 0
	lineData = None
	searchStart = 0
	searchEnd = -1
	listIndex = 0
	listCtrl = None
	dealOnce = None
	regList = []
	nameList = []
	OldEncodeName = None

def searchLine(var):
	if var.searchStart > 0:
		searchData = var.lineData[var.searchStart:var.searchEnd]
	else:
		searchData = var.lineData
	for regItem in var.regList:
		regType = regItem[1]
		value = regItem[0]
		if regType == 'skip':
			# 跳过
			if re.search(value, searchData): break #已匹配则停止
		else:
			# 搜索
			tmpDic = {}
			matched = False
			iter = re.finditer(value, searchData) 
			for r in iter:
				#print(r.groups())
				for i in range(1, len(r.groups())+1):
					if r.group(i) == None: continue
					start = r.start(i) + var.searchStart
					end = r.end(i) + var.searchStart
					if var.OldEncodeName: # bin
						text = var.lineData[start:end].decode(var.OldEncodeName)
					else: # txt
						text = var.lineData[start:end]
					#0行数，1起始字符下标（包含），2结束字符下标（不包含）
					ctrl = {'pos':[var.contentIndex, start, end]}
					tmpDic[start] = [text, ctrl]
					#检查命名
					key = None
					for name, index in r.re.groupindex.items():
						if i == index: key = name
					if not key:
						pass
					elif key.startswith('name') or text in var.nameList:
						ctrl['isName'] = True #名字标记
					elif key.startswith('unfinish'):
						ctrl['unfinish'] = True
					matched = True
			if matched :
				#按文本中顺序处理
				for key in sorted(tmpDic.keys()):
					value = tmpDic[key]
					if var.dealOnce(value[0], var.listIndex):
						var.listIndex += 1
						var.listCtrl.append(value[1])
				break #已匹配则停止

# ---------------- Group: TXT -------------------
def parseImp(content, listCtrl, dealOnce):
	var = ParseVar()
	var.listIndex = 0
	var.listCtrl = listCtrl
	var.dealOnce = dealOnce
	#print(len(content))
	regDic = GetG('Var').regDic
	var.nameList = GetG('Var').nameList
	var.regList = []
	for key, value in regDic.items():
		if re.search('skip', key):
			var.regList.append([value, 'skip'])
		elif re.search('search', key):
			var.regList.append([value, 'search'])
	for contentIndex in range(len(content)):
		#if contentIndex < 1: continue 
		lineData = content[contentIndex][:-1] #不检查末尾换行
		# 每行
		#print('>>> Line ' + str(contentIndex), ': ', lineData)
		if lineData == '': continue #空白行
		var.contentIndex = contentIndex
		var.lineData = lineData
		searchLine(var)

# -----------------------------------
def replaceOnceImp(content, lCtrl, lTrans):
	#print(lCtrl)
	#print(lTrans)
	num = len(lCtrl)
	for i in range(num):
		# 位置
		ctrl = lCtrl[i]
		posData = ctrl['pos']
		contentIndex = posData[0]
		start = posData[1]
		end = posData[2]
		trans = lTrans[i]
		#写入new
		strNew = content[contentIndex][:start] + trans + content[contentIndex][end:]
		#print(strNew)
		content[contentIndex] = strNew
		return True