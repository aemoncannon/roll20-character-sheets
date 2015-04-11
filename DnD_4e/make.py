import pyratemp

t = pyratemp.Template(filename="DnD_4e.html.template")
result = t()
f = open("DnD_4e.html", "w")
f.write(result)
f.close()

