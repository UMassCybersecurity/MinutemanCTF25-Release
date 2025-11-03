with open("transmission_raw", "r") as fd:
    content = fd.read()
    content = bytes.fromhex(content)
    content = content.decode("utf-16")
    index = content.find("MINUTEMAN")
    print(content[index:index+100])
