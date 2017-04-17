import pyglet
from pyglet.gl import *
from collections import OrderedDict
from time import time, sleep
from math import *
#from threading import *

from generic_gfx import *

# REQUIRES: AVBin
pyglet.options['audio'] = ('alsa', 'openal', 'silent')
key = pyglet.window.key
# xfce4-notifyd 
debug = True

class CustomGroup(pyglet.graphics.Group):
	def set_state(self):
		#pyglet.gl.glLineWidth(5)
		#glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
		#glColor4f(1, 0, 0, 1) #FFFFFF
		#glLineWidth(1)
		#glEnable(texture.target)
		#glBindTexture(texture.target, texture.id)
		pass

	def unset_state(self):
		glLineWidth(1)
		#glDisable(texture.target)

class player(Spr):
	def __init__(self, x, y):
		super(player, self).__init__(x=x, y=y)
		self.group = CustomGroup()

		self.target_angle = 0
		self.angle = 0
		self.speed = 160 # pixels/sec
		self.multiplier = 1
		self.turn_speed = 125 # deg/sec
		self.delayed_follow = 3 # How many frames between index(0) -> idnex(1) -> ...
		self.x, self.y = x, y

		self.blobs = {}
		self.offsets = {}
		self.history = []

		self.last_update = time()

		self.add_position(x, y)
		for i in range(50):
			self.add_position(x, y)
		#self.add_position(x, y)

	def add_position(self, x, y):

		RED = (255, 0, 0)
		WHITE = (255, 255, 255)

		colors = ()#255,0,0

		sides = 50
		radius = 25

		deg = 360/sides
		points = ()#x, y # Starting point is x, y?
		
		prev = None
		for i in range(sides):
			#points += x, y

			
			n = ((deg*i)/180)*pi # Convert degrees to radians
			point = int(radius * cos(n)) + x, int(radius * sin(n)) + y

			if prev:
				points += x, y
				points += prev
				points += point
				colors += (255, i*int(255/sides), 0)*3

			#if prev:
			#	points += int(radius * cos(n)) + x, int(radius * sin(n)) + y

			#colors += (255, i*int(255/sides), 0)
			#self.offsets[i] = int(radius * cos(n)), int(radius * sin(n))
		
			prev = point

		points += x, y
		points += prev
		points += points[2:4]
		colors += (255, 0, 255)*3

		self.offsets[len(self.blobs)] = points

		print(int(len(points)/2/3))
		print(len(points), points)
		print(len(colors))

		self.blobs[len(self.blobs)] = {
			'blob' : pages[active_page].add(int(len(points)/2), pyglet.gl.GL_TRIANGLES, self.group, ('v2i/stream', points), ('c3B', colors)),
			'x' : x,
			'y' : y
		}

	def update(self):
		time_last_render = time() - self.last_update
		self.last_update = time()

		if self.speed == 0:
			return

		speed_factor = time_last_render * (self.speed*self.multiplier)
		turn_factor = time_last_render * self.turn_speed

		# if int(self.angle) != int(self.target_angle):
		# 	a = self.angle - 180
		# 	ta = self.target_angle - 180
		# 	abso = fabs(a - ta)
		# 	if abso == a - ta:
		# 		self.angle -= turn_factor
		# 	else:
		# 		self.angle += turn_factor

		# 	self.angle %= 360

		self.target_angle = ((atan2(mouse_y-self.y, mouse_x-self.x)/pi*180)+360)%360
		a = self.target_angle - self.angle
		a = (a + 180) % 360 - 180

		#print()

		#if a != 0:
		#	print(a, self.target_angle, self.angle)

		a = max(min(a, turn_factor), 0-turn_factor)
		self.angle += (a+360)
		self.angle %= 360

		x = cos(((self.angle)/180)*pi)
		y = sin(((self.angle)/180)*pi)

		self.x += x * speed_factor
		self.y += y * speed_factor

		for index, obj in self.blobs.items():
			if index == 0:
				self.history.insert(0, (self.x, self.y))
				self.history = self.history[:len(self.blobs)*self.delayed_follow]

			#print(index, list(obj['blob'].vertices))
			for i in range(0, len(obj['blob'].vertices)):
				if index == 0:
					if i%2:
						obj['blob'].vertices[i] = int(self.y + self.offsets[index][i])
					else:
						obj['blob'].vertices[i] = int(self.x + self.offsets[index][i])
					# X:
					#obj['blob'].vertices[i+0] = int(self.x + self.offsets[i//2][0])
					#Y:
					#obj['blob'].vertices[i+1] = int(self.y + self.offsets[i//2][1])
				elif len(self.history) > index*self.delayed_follow:
					if i%2:
						obj['blob'].vertices[i] = int(self.history[index*self.delayed_follow][1] + self.offsets[index][i])
					else:
						obj['blob'].vertices[i] = int(self.history[index*self.delayed_follow][0] + self.offsets[index][i])
					# X:
					#obj['blob'].vertices[i+0] = int(self.history[index*self.delayed_follow][0] + self.offsets[i//2][0])
					#Y:
					#obj['blob'].vertices[i+1] = int(self.history[index*self.delayed_follow][1] + self.offsets[i//2][1])
			#sleep(0.5)

class main(pyglet.window.Window):
	def __init__ (self, demo=False):
		super(main, self).__init__(800, 600, fullscreen = False, vsync = True)
		#print(self.context.config.sample_buffers)
		self.x, self.y = 0, 0

		self.sprites = OrderedDict()
		self.pages = OrderedDict()
		self.pages['default'] = pyglet.graphics.Batch()
		self.active_page = 'default'
		__builtins__.__dict__['pages'] = self.pages
		__builtins__.__dict__['active_page'] = self.active_page

		self.merge_sprites_dict = {}

		## == Demo sprites:
		if demo:
			#self.sprites['bg'] = Spr('background.jpg')
			#self.sprites['test'] = Spr(x=0, y=0, height=self.height, moveable=False)
			self.sprites['player'] = player(0, 0)

		#glTranslatef(100, 100, 100)

		self.key_down = {}
		self.drag = False
		self.active = None, None
		self.alive = 1
		self.mouse_x = 0
		self.mouse_y = 0
		__builtins__.__dict__['mouse_x'] = 0
		__builtins__.__dict__['mouse_y'] = 0

		self.fps = 0
		self.last_fps = time()
		self.fps_label = pyglet.text.Label(str(self.fps) + ' fps', font_size=12, x=3, y=self.height-35)
		self.player_info = pyglet.text.Label(str(self.sprites['player'].x) + ',' + str(self.sprites['player'].y), font_size=12, x=3, y=self.height-18)
		self.mouse_pos = pyglet.text.Label(str(self.mouse_x) + ', ' + str(self.mouse_y), font_size=12, x=3, y=self.height-55)

		self.keymap = 0
		self.keymapTranslation = {
			# bitVal : angle.degrees
			#0 : 0, # <- Turns turning off
			5 : 45,
			1 : 90,
			9 : 135,
			8 : 180,
			10 : 225,
			2 : 270,
			6 : 315,
			4 : 360,
		}

		#self.draw_line(1,2)

	def on_draw(self):
		self.render()

	def on_close(self):
		self.alive = 0

	def add_page(self, name, sprites):
		self.pages[name] = sprites

	def swap_page(self, name):
		if name in self.pages:
			self.pages['_active_'] = name

	def add_merge_sprites(self, sprites):
		for key, val in sprites.items():
			self.merge_sprites_dict[key] = val

	def merge_sprites(self):
		## We're using self.merge_sprites_dict here so that sub-items
		## can add back new graphical content but not in the active
		## pool of rendered objects, instead we'll lift them in for
		## the subitems so they don't have to worry about cycles
		## or how to deal with them.

		if len(self.merge_sprites_dict) > 0:
			merge_sprite = self.merge_sprites_dict.popitem()
			#if merge_sprite[0] == 'input':
			#	self.requested_input = merge_sprite[1][0]
			#	self.sprites[merge_sprite[0]] = merge_sprite[1][1]
			#else:
			self.sprites[merge_sprite[0]] = merge_sprite[1]
			## TODO: _active_ might be None.
			self.pages[self.pages['_active_']].append(merge_sprite[0])

	def on_mouse_motion(self, x, y, dx, dy):
		self.mouse_x = x
		self.mouse_y = y
		self.mouse_pos.text = str(self.mouse_x) + ', ' + str(self.mouse_y)
		__builtins__.__dict__['mouse_x'] = self.mouse_x
		__builtins__.__dict__['mouse_y'] = self.mouse_y

		#for sprite_name, sprite in self.sprites.items():
		#	if sprite:
		#		sprite_obj = sprite.click_check(x, y)
		#		if sprite_obj:
		#			sprite_obj.hover(x, y)
		#		else:
		#			#TODO: Check why not sprite_obj?
		#			sprite.hover_out(x, y)

	def on_mouse_release(self, x, y, button, modifiers):
		if button == 1:
			pass
		self.sprites['player'].multiplier=1
	def on_mouse_press(self, x, y, button, modifiers):
		if button == 1 or button == 4:
			pass
		self.sprites['player'].multiplier=2

	def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
		self.drag = True

		## Remake:
		## - If the first object is moveable=False, do a connection.
		#if self.active[1] and self.multiselect == False and hasattr(self.active[1], 'link'):
		#	self.lines['link'] = ((self.active[1].x+(self.active[1].width/2), self.active[1].y+(self.active[1].height/2)), (x,y))
		#elif self.multiselect:
		#	for obj in self.multiselect:
		#		self.sprites[obj].move(dx, dy)
		if None not in self.active:
			self.active[1].move(dx, dy)
		#for obj in self.multiselect:
		#	self.sprites[obj].move(dx, dy)

	def on_key_release(self, symbol, modifiers):
		if symbol == key.LCTRL:
			self.multiselect = False

		del self.key_down[symbol]

		if key.UP == symbol:
			self.keymap ^= 1
		if key.DOWN == symbol:
			self.keymap ^= 2
		if key.RIGHT == symbol:
			self.keymap ^= 4
		if key.LEFT == symbol:
			self.keymap ^= 8

		if self.keymap in self.keymapTranslation:
			self.sprites['player'].target_angle = self.keymapTranslation[self.keymap]
			#print('Release:', self.keymap, self.sprites['player'].target_angle)

	def on_key_press(self, symbol, modifiers):
		if symbol == key.ESCAPE: # [ESC]
			self.alive = 0

		if symbol == key.SPACE:
			self.sprites['player'].speed = 0

		self.key_down[symbol] = time()

		if key.UP in self.key_down:
			self.keymap |= 1
		if key.DOWN in self.key_down:
			self.keymap |= 2
		if key.RIGHT in self.key_down:
			self.keymap |= 4
		if key.LEFT in self.key_down:
			self.keymap |= 8

		if self.keymap in self.keymapTranslation:
			self.sprites['player'].target_angle = self.keymapTranslation[self.keymap]
			#print('Press:', self.keymap, self.sprites['player'].target_angle)

	def draw_line(self, xy, dxy):
		self.pages[self.active_page].add(2, pyglet.gl.GL_LINES, None,
			('v2i', (10, 15, 300, 305))
		)
		#glColor4f(0.2, 0.2, 0.2, 1)
		#glBegin(GL_LINES)
		#glVertex2f(xy[0], xy[1])
		#glVertex2f(dxy[0], dxy[1])
		#glEnd()

	def render(self):
		self.clear()
		#self.bg.draw()

		self.merge_sprites()

		if not self.active_page in self.pages:
			print('Defaulting back to default batch')
			self.pages['default'].draw()

		else:
			#print('Rendering: {page}'.format(**{'page' : self.active_page}))
			self.pages[self.active_page].draw()


		#for symbol, xtime in self.key_down.items():
		#	if time() - xtime > 0.02:

		self.sprites['player'].update()

		#		self.key_down[symbol] = time()
		self.player_info.text = str(int(self.sprites['player'].x)) + ', ' + str(int(self.sprites['player'].y)) + ' [' + str(int(self.sprites['player'].angle)) + '/' + str(int(self.sprites['player'].target_angle)) + ']'

		self.fps += 1
		if time()-self.last_fps > 1:
			self.fps_label.text = str(self.fps) + ' fps'
			self.fps = 0
			self.last_fps = time()

		#print(self.sprites['player'].history)


		self.fps_label.draw()
		self.player_info.draw()
		self.mouse_pos.draw()
		self.flip()

	def run(self):
		while self.alive == 1:
			self.render()

			# -----------> This is key <----------
			# This is what replaces pyglet.app.run()
			# but is required for the GUI to not freeze
			#
			event = self.dispatch_events()

if __name__ == '__main__':
	x = main(demo=True)
	x.run()