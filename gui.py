from PIL import Image, ImageTk
from tkinter import Tk, Message, ttk, Button, Canvas, Y, W, LEFT, S, CENTER, PhotoImage, SUNKEN, RAISED
from tkinter.filedialog import askopenfilename
from colorsys import rgb_to_hsv

class GUI:
	"""
	A class to represent the gui for this program.
	"""
	def __init__(self):
		# There may be other compatible types I am not aware of
		self.image_types = ['png', 'jpg', 'gif', 'jpeg']

		# Create window
		self.window = Tk()
		self.window.title("Image Saturation Reader")

		# Set default variables
		self.current_image_name = "None Selected"
		self.current_image = None
		self.current_mode = 'area'
		self.corners = []
		self.sight_lines = []

		# Find screen height
		width = self.window.winfo_screenwidth()
		height = self.window.winfo_screenheight()
		self.width = width - (width // 2)
		self.height = height - (height // 2)

		# Populate window
		self._generate_window()

		# Bind events
		self.canvas.bind('<Motion>', self.motion)
		self.canvas.bind('<Leave>', self.leave)
		self.canvas.bind('<Button-1>', self.click)

		# Final stylizations
		self.area_mode_button.config(relief=SUNKEN)
	
	def click(self, event):
		"""
		Clicking within the canvas.
		"""
		if self.current_image is not None:
			x, y = event.x, event.y
			if self.current_mode == 'area':
				if not self.corners:
					self.corners.append(self.canvas.create_oval(x-2, y-2, x+2, y+2, fill='white'))
				elif len(self.corners) == 1:
					self.corners.append(self.canvas.create_oval(x-2, y-2, x+2, y+2, fill='white'))
					x1, y1, *_ = self.canvas.coords(self.corners[0])
					x2, y2, *_ = self.canvas.coords(self.corners[1])
					self.get_pixel_data(x1, y1, x2, y2)
				else:
					self.clear_drawings()
					self.clear_drawing_data()
					self.corners.append(self.canvas.create_oval(x-2, y-2, x+2, y+2, fill='white'))
			elif self.current_mode == 'pixel':
				self.get_pixel_data(x, y, x, y)

	def get_pixel_data(self, x1, y1, x2, y2):
		x1 = round(x1)
		y1 = round(y1)
		x2 = round(x2)
		y2 = round(y2)
		if x2 < x1:
			x1, x2 = x2, x1
		if y2 < y1:
			y1, y2 = y2, y1
		totalSaturation = 0
		c = 0
		for y in range(y1, y2 + 1):
			for x in range(x1, x2 + 1):
				r, g, b, *_ = self.current_image.getpixel((x, y))
				totalSaturation += rgb_to_hsv(r, g, b)[1]
				c += 1
		avg = round((totalSaturation / c) * 100, 2)
		self.write_pixel_data(avg, c)

	def write_pixel_data(self, avg, c):
		self.num_pixels.configure(text='# Pixels: ' + str(c))
		self.saturation.configure(text='Saturation: ' + str(avg) + '%')

	def leave(self, event):
		self.x.configure(text='x: ')
		self.y.configure(text='y: ')

	def motion(self, event):
		if self.current_image is not None:
			x, y = event.x + 1, event.y + 1
			self.x.configure(text='x: ' + str(x))
			self.y.configure(text='y: ' + str(y))
			if len(self.corners) == 1:
				self.draw_sight_lines(x, y)
	
	def draw_sight_lines(self, x, y):
		for line in self.sight_lines:
				self.canvas.delete(line)
		lx, ly, *_ = self.canvas.coords(self.corners[0])
		lx += 2
		ly += 2
		self.sight_lines.append(self.canvas.create_line(lx, ly, x, ly, dash=(3, 3)))
		self.sight_lines.append(self.canvas.create_line(lx, ly, lx, y, dash=(3, 3)))
		self.sight_lines.append(self.canvas.create_line(x, ly, x, y, dash=(3, 3)))
		self.sight_lines.append(self.canvas.create_line(lx, y, x, y, dash=(3, 3)))
			
	def _generate_window(self):
		"""
		Generate the components inside the window.
		"""
		# Left-side information panel
		info_panel = ttk.Frame(self.window)

		# Create components inside left panel
		choose_image = Button(info_panel, text='Choose Image', command=self.choose_image)
		image_label = Message(info_panel, text='Image:', width=40)
		self.image_name = Message(info_panel, text=self.current_image_name, width=100)
		self.image_width = Message(info_panel, text='W: ', width=50)
		self.image_height = Message(info_panel, text='H: ', width=50)
		self.separator = Message(info_panel, text='=======', width=75)
		self.x = Message(info_panel, text='x: ', width=40)
		self.y = Message(info_panel, text='y: ', width=40)
		self.num_pixels = Message(info_panel, text='# Pixels: ', width = 50)
		self.saturation = Message(info_panel, text='Saturation: ', width=75)
		self.pixel_mode_button = Button(info_panel, text='Pixel Mode', command=self.pixel_mode)
		self.area_mode_button = Button(info_panel, text='Area Mode', command=self.area_mode)

		# Place the components inside left panel
		choose_image.grid(padx=5, pady=5)
		image_label.grid(sticky=W)
		self.image_name.grid(sticky=W)
		self.image_width.grid(sticky=W)
		self.image_height.grid(sticky=W)
		self.separator.grid()
		self.x.grid(sticky=W)
		self.y.grid(sticky=W)
		self.num_pixels.grid(sticky=W)
		self.saturation.grid(sticky=W)
		self.area_mode_button.grid()
		self.pixel_mode_button.grid()

		# Create right side
		self.canvas = Canvas(self.window, width=self.width, height=self.height, bg='lightblue')

		# Add two sides to final window
		info_panel.pack(side=LEFT, fill=Y)
		self.canvas.pack()

	def choose_image(self):
		self.current_image_name = askopenfilename()
		if self.current_image_name.split('.')[-1] in self.image_types:
			self.image_name.configure(text=self.current_image_name.split('/')[-1])
			self.open_image()

	def clear_drawing_data(self):
		self.corners = []
		self.sight_lines = []

	def clear_drawings(self):
		for line in self.sight_lines:
			self.canvas.delete(line)
		for dot in self.corners:
			self.canvas.delete(dot)

	def open_image(self):
		self.current_image = Image.open(self.current_image_name)
		current_image_tk = ImageTk.PhotoImage(self.current_image)
		width = current_image_tk.width()
		height = current_image_tk.height()
		self.canvas.config(width=width - 4, height=height - 4)
		self.canvas.create_image(round(width / 2), round(height / 2), anchor=CENTER, image=current_image_tk)
		self.canvas.image = current_image_tk

	def pixel_mode(self):
		self.clear_drawings()
		self.clear_drawing_data()
		self.pixel_mode_button.config(relief=SUNKEN)
		self.area_mode_button.config(relief=RAISED)
		self.current_mode = 'pixel'
	
	def area_mode(self):
		self.clear_drawings()
		self.clear_drawing_data()
		self.area_mode_button.config(relief=SUNKEN)
		self.pixel_mode_button.config(relief=RAISED)
		self.current_mode = 'area'


if __name__ == '__main__':
	ui = GUI()
	ui.window.mainloop()