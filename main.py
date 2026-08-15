from card import Card

Card.pack('example/img.jpg', "Hello world!")
manifest = Card.unpack('example/img.card')

print(manifest)
