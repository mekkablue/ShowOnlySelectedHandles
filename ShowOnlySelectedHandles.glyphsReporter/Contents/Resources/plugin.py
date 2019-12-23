# encoding: utf-8

###########################################################################################################
#
#
#	Reporter Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Reporter
#
#
###########################################################################################################

from __future__ import division, print_function, unicode_literals
import objc
from GlyphsApp import *
from GlyphsApp.plugins import *

class ShowOnlySelectedHandles(ReporterPlugin):
	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize({
			'en': u'Only Selected Handles',
			'de': u'Nur ausgewählte Anfasser',
			'fr': u'seulement les poignées sélectionnées',
			'es': u'los manejadores seleccionados',
		})
		self.selectedColor = NSColor.labelColor() # NSColor.colorWithRed_green_blue_alpha_(0.0, 0.0, 0.0, 1.0)
		self.unselectedColor = NSColor.secondaryLabelColor() # NSColor.colorWithRed_green_blue_alpha_(0.4, 0.4, 0.4, 1.0)
	
	@objc.python_method
	def conditionsAreMetForDrawing(self):
		"""
		Don't activate if text or pan (hand) tool are active.
		"""
		currentController = self.controller.view().window().windowController()
		if currentController:
			tool = currentController.toolDrawDelegate()
			textToolIsActive = tool.isKindOfClass_( NSClassFromString("GlyphsToolText") )
			handToolIsActive = tool.isKindOfClass_( NSClassFromString("GlyphsToolHand") )
			if not textToolIsActive and not handToolIsActive: 
				return True
		return False
	
	@objc.python_method
	def foreground(self, layer):
		if self.conditionsAreMetForDrawing():
			for thisPath in layer.paths:
				nodeCount = len(thisPath.nodes)
				for i in range(nodeCount):
					currNode = thisPath.nodes[i]
					if currNode.selected:
						# always draw selected nodes
						self.selectedColor.set()
						self.drawHandleForNode(currNode)
					elif currNode.type != OFFCURVE:
						# always draw oncurves
						self.unselectedColor.set()
						self.drawHandleForNode(currNode)
					else:
						# draw handles surrounding the selection
						prevNode = thisPath.nodes[(i-1)%nodeCount]
						nextNode = thisPath.nodes[(i+1)%nodeCount]
						if prevNode.selected or nextNode.selected:
							self.unselectedColor.set()
							self.drawHandleForNode(currNode)
	
	@objc.python_method
	def background(self, layer):
		if self.conditionsAreMetForDrawing():
			# set color
			self.unselectedColor.set()

			# save original line width setting
			oldLineWidth = NSBezierPath.lineWidth()
			NSBezierPath.setLineWidth_(1.0/self.getScale())
		
			for thisPath in layer.paths:
				nodeCount = len(thisPath.nodes)
				for i in range(nodeCount):
					handle = thisPath.nodes[i]
					if handle.type == OFFCURVE:
						prevNode = thisPath.nodes[(i-1)%nodeCount]
						nextNode = thisPath.nodes[(i+1)%nodeCount]
						if handle.selected or prevNode.selected or nextNode.selected:
							nearestOnCurve = prevNode if prevNode.type!=OFFCURVE else nextNode
							NSBezierPath.strokeLineFromPoint_toPoint_(
								handle.position,
								nearestOnCurve.position,
							)
		
			# restore original line width
			NSBezierPath.setLineWidth_(oldLineWidth)
				
	@objc.python_method
	def drawHandleForNode(self, node):
		# calculate handle size:
		handleSizes = (5, 8, 12) # possible user settings
		handleSizeIndex = Glyphs.handleSize # user choice in Glyphs > Preferences > User Preferences > Handle Size
		handleSize = handleSizes[handleSizeIndex]*self.getScale()**-0.9 # scaled diameter
	
		# offcurves are a little smaller:
		if node.type == OFFCURVE:
			handleSize *= 0.8
	
		# selected handles are a little bigger:
		if node.selected:
			handleSize *= 1.45
	
		# draw disc inside a rectangle around point position:
		position = node.position
		rect = NSRect()
		rect.origin = NSPoint(position.x-handleSize/2, position.y-handleSize/2)
		rect.size = NSSize(handleSize, handleSize)
		if node.type == OFFCURVE or node.smooth:
			NSBezierPath.bezierPathWithOvalInRect_(rect).fill()
		else:
			NSBezierPath.bezierPathWithRect_(rect).fill()
	
	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
