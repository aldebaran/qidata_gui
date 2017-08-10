# -*- coding: utf-8 -*-

def test_open_command(jpg_file_path, open_command_parser):
	parsed_arguments = open_command_parser.parse_args([
	                                                      jpg_file_path
	                                                  ])
	assert(None == parsed_arguments.writer)

	parsed_arguments = open_command_parser.parse_args([
	                                                      jpg_file_path,
	                                                      "-w"
	                                                  ])
	assert("" == parsed_arguments.writer)

	parsed_arguments = open_command_parser.parse_args([
	                                                      "-w",
	                                                      "jdoe",
	                                                      jpg_file_path
	                                                  ])
	assert("jdoe" == parsed_arguments.writer)