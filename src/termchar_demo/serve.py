from textual_serve.server import Server

server = Server("python -m termchar_demo.app")
server.serve()
