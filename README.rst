Script to fix SSI include paths.
================================

SSI disallows ".." in include paths, and while Apache doesn't seem to
mind them that much, nginx refuses to include such a file. This script
takes a file path and a document root path as parameters, and replaces
such include paths with ones which are allowed.
