# run in python3
import os, math, io, zipfile
from audiolazy import midi2freq
from os.path import basename
from solid import *
from solid.utils import *
from trianglesolver import solve, degree

## Sources for the math:
## http://www.rwgiangiulio.com/math/
## http://www.fonema.se/

def assembly(startpoint, Wb, L, T, Ws, Cw, Cl, Fl, HL, LL, IW, TU, SD, pipe):
	use(os.getcwd() + "/static/prism.scad")
	
	back = union()(
		translate([startpoint+0,0,0])(
	    		cube([Wb, L, T], center = False)
		)
    	)
	side1 = union()(
		translate([startpoint+(Wb+10),0,0])(
	    		cube([Ws, L, T], center = False)
		)
    	)
	side2 = union()(
		translate([startpoint+(Wb+Ws+2*10),0,0])(
	    		cube([Ws, L, T], center = False)
		)
    	)
	cover = union()(
		translate([startpoint+(Wb+2*Ws+3*10),0,0])(
	    		cube([Cw, Cl, T], center = False)
		)
    	)
	front = union()(
		translate([startpoint+(Wb+2*Ws+3*10),Cl+10,0])(
			difference()(
	    		cube([Wb, Fl, T], center = False),
			translate([-1,-1,HL])(
				prism(l = LL+1, w = Wb+2, h = T)(
				)
			)
			)			
		)
    	)
	bottom = union()(
		translate([startpoint+(2*Wb+2*Ws+4*10),0,0])(
			difference()(
	    		cube([IW, IW, T]),
			translate([(IW/2),(IW/2),-1])(	
				cylinder(r=TU, h=T+2)
			)
			)
		)
    	)
	inside = union()(
		translate([startpoint+(2*Wb+2*Ws+4*10),IW+10,0])(
			difference()(
	    		cube([IW, IW, T], center = False),
			translate([0,0,(T/2)])(
				prism(l = (T/2), w = Wb+2, h = (T/2))(
				)
			)
			)		
		)
    	)
	if pipe == "Closed":
		top = union()(
			translate([startpoint+(2*Wb+2*Ws+4*10),2*(IW+10),0])(
				difference()(
		    		cube([IW-2, IW-2, T], center = False),
				translate([((IW-2)/2),((IW-2)/2),0.25*T])(	
					cylinder(r=SD+0.03, h=0.75*T+1)	
				)
				)
			)
    		)
	
		return union()(back, side1, side2, cover, front, bottom, inside, top)
	elif pipe == "Open":
		return union()(back, side1, side2, cover, front, bottom, inside)

def GenerateOpenSCAD(var, cs, SA, HL, pipe, TU, SD, M, F, T):
	SEGMENTS = 48						# solidpython variable

	for midinr in var:
		inputorder = var.index(midinr)
		f = midi2freq(int(midinr))			# get frequency by midi nr
		WL = cs/f 					# wavelength in mm					
		ILA = WL/2					# internal length
		L69 = ((cs/midi2freq(69))/2)			# internal length of midi nr 69
		IW = L69 * 2**((69-int(midinr))/M)/12		# internal width
		IL = cs / (2 * f)				# calculate internal length

		def openclosedmeasurements():
			if pipe == "Closed":
				l = 0.52*IL+IW+F
				mh = (3.018-(0.233*(math.log(f))))**5
				return l, mh
			elif pipe == "Open":
				l = 1.03*IL-IW+F
				mh = 550/2**(math.log(f))
				return l, mh	 

		L, MH = openclosedmeasurements()		# L = length; MH=Mouth Height

		a,b,c,A,B,C = solve(a=T-HL, A=SA*degree, B=90*degree)
		LL = c						# length labium

		Wb = IW+2*T					# width back
		Ws = IW					        # width sides

		BPl = F+IW					# bottom plug length
		BPw = IW					# bottom plug width
		BPt = IW					# bottom plug thickness

		Cl = F+IW					# cover length
		Cw = IW + 2*T					# cover width

		Gl = F+2*IW					# gasket length
		Gw = IW+2*T					# gasket width

		Fl = L-MH-F-IW					# Front length

		if inputorder == 0:
			startpoint = 0
			scadcode = assembly(startpoint, Wb, L, T, Ws, Cw, Cl, Fl, HL, LL, IW, TU, SD, pipe)
			startpoint = 2*Wb+2*Ws+IW+5*10
		else:
			scadcode = scadcode.add(assembly(startpoint, Wb, L, T, Ws, Cw, Cl, Fl, HL, LL, IW, TU, SD, pipe))
			startpoint = startpoint+(2*Wb+2*Ws+IW+5*10)	

	scad_string_dirty=scad_render(scadcode)
	scad_string = scad_string_dirty.replace(scad_string_dirty[scad_string_dirty.find("<")+1:scad_string_dirty.find(">")],basename(scad_string_dirty[scad_string_dirty.find("<")+1:scad_string_dirty.find(">")]))

	static_directory = '/static'
	out_dir = os.getcwd() + static_directory
	in_memory = io.BytesIO()
	z = zipfile.ZipFile(in_memory, 'w', zipfile.ZIP_DEFLATED)
	z.writestr('pipes.scad', scad_string)
	z.write(os.path.join(out_dir, "prism.scad"), "prism.scad")
	z.close()
	in_memory.seek(0)
	return(in_memory)
