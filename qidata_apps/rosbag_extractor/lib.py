# Standard libraries
import os
import math

# Third-party libraries
try:
	import cv2
	from cv_bridge.core import CvBridge
	from geometry_msgs.msg import TransformStamped
	from rosbag import Bag as RosBag
	from tf2_py import _tf2, TransformException
	_rosbag_conversion_enabled = True
except ImportError:
	_rosbag_conversion_enabled = False

# Local modules
import qidata
from qidata import QiDataSet, DataType
from qidata.metadata_objects import TimeStamp, Transform

if _rosbag_conversion_enabled:

	def addMsgToBuffer(tf_buffer, msg):
		"""
		Add TF message to the TF buffer.

		:param tf_buffer: buffer containing TF data
		:type  tf_buffer: _tf2.BufferCore()
		:param msg: TF message
		:type  msg: tf.TFMessage
		"""
		for i in range(0,len(msg.transforms)):
			try:
				m = TransformStamped()
				#### There is a bug in geometry_msgs, messages are no
				#### longer properly read if coming from a bag .....
				m.header = msg.transforms[i].header
				m.child_frame_id = msg.transforms[i].child_frame_id
				m.transform.translation.x = msg.transforms[i].transform.translation.x
				m.transform.translation.y = msg.transforms[i].transform.translation.y
				m.transform.translation.z = msg.transforms[i].transform.translation.z
				m.transform.rotation.x = msg.transforms[i].transform.rotation.x
				m.transform.rotation.y = msg.transforms[i].transform.rotation.y
				m.transform.rotation.z = msg.transforms[i].transform.rotation.z
				m.transform.rotation.w = msg.transforms[i].transform.rotation.w

				tf_buffer.set_transform(m, "no callerid");
			except TransformException, e:
				print "Failed to set received transform from %s to %s: %s\n"%(
				           msg.transforms[i].child_frame_id,
				           msg.transforms[i].header.frame_id,
				           e.what()
				       )

	def addFileToStream(dataset, stream_name, time_file_pair):
		"""
		Add files to a dataset stream, create it if non-existant

		:param dataset: Open dataset to modify
		:type  dataset: qidata.qidataset.QiDataSet
		:param stream_name: Name of the stream to create/modify
		:type  stream_name: str
		:param time_file_pair: Pair of timestamp and file
		:type  time_file_pair: 2-uple
		"""
		try:
			dataset.addToStream(
			  stream_name,
			  time_file_pair
			)
		except KeyError:
			dataset.createNewStream(
			  stream_name,
			  [time_file_pair]
			)

	def makeQiDataSetFromROSbag(rosbag_path, topics_to_save, ds_context):
		"""
		Create a QiDataSet from a ROSbag

		:param rosbag_path: Path of the bag
		:type rosbag_path: str
		:param topics_to_save: Map between topics and (types, filename prefixes)
		:type topics_to_save: dict
		"""
		# Create an appropriate folder from the bag name
		rosbag_path = os.path.abspath(rosbag_path)
		output_folder = os.path.splitext(os.path.abspath(rosbag_path))[0]
		if not os.path.isdir(output_folder):
			os.mkdir(output_folder)

		# Initialize it as a QiDataSet
		qs = QiDataSet(output_folder, "w")

		# Initialize a TF buffer
		tf_buffer = _tf2.BufferCore()

		with RosBag(rosbag_path, 'r') as bag:
			# Retrieve information about the bag's content
			topics_info = bag.get_type_and_topic_info()[1]

			# Prepare needed structures
			counter = dict() # file counter for each topics
			filename_gen = dict() # filename pattern for each topic
			current_state = dict() # Holds the current file for each topic
			for topic, topic_details in topics_info.iteritems():
				if not topics_to_save.has_key(topic):
					continue
				filename_gen[topic] = topics_to_save[topic][0]+"_%%0%dd.png"%(
				                        int(
				                          math.ceil(
				                            math.log10(
				                              topic_details[1]
				                            )
				                          )
				                        )
				                      )
				counter[topic] = 0
				current_state[topic] = None

			# Initialize openCV-ROS bridge
			bridge = CvBridge()

			# Walk through the bag a first time to construct the tf buffer
			for (_, msg, timestamp) in bag.read_messages(topics='/tf'):
				addMsgToBuffer(tf_buffer, msg)

			# Remove the tf from the meaningful topics
			topics_info.pop("/tf")

			# Then walk again through the bag and extract the data
			for (topic_name, msg, timestamp) in bag.read_messages(
			                                        topics=topics_info.keys()):
				if not topics_to_save.has_key(topic_name):
					continue

				if topics_info[topic_name][0] == "sensor_msgs/Image":
					# Message is an image, so retrieve it with CvBridge
					cv_image = bridge.imgmsg_to_cv2(
					             msg,
					             desired_encoding="passthrough"
					           )
					if msg.encoding == "rgb8":
						# Image is RGB but openCV handles images as if they are
						# in BGR. So we convert this image, to make it BGR (and
						# have openCV happy)
						cv_converted_image = cv2.cvtColor(
						                       cv_image,
						                       cv2.COLOR_BGR2RGB
						                     )
					else:
						# This is probably BGR, or GRAY, so leave it like this
						# TODO: Some checks for other color type might be useful
						# one day
						cv_converted_image = cv_image

					# Save image
					filename = filename_gen[topic_name]%counter[topic_name]
					cv2.imwrite(
					  os.path.join(
					    output_folder,
					    filename
					  ),
					  cv_converted_image
					)

					# odom is the target_frame because we want the transform to
					# pass object in the camera frame into the world frame. Or
					# simply now the camera position ((0,0,0) in its own frame)
					# in the world frame.
					ros_tf = tf_buffer.lookup_transform_core(
					           "odom",
					           msg.header.frame_id,
					           msg.header.stamp
					         )

					# Set the file timestamp, transform and type
					with qidata.open(os.path.join(
					       output_folder,
					       filename
					    ),"w") as _f:
						_f.timestamp.seconds = msg.header.stamp.secs
						_f.timestamp.nanoseconds = msg.header.stamp.nsecs

						_f.transform.translation.x = ros_tf.transform.translation.x
						_f.transform.translation.y = ros_tf.transform.translation.y
						_f.transform.translation.z = ros_tf.transform.translation.z
						_f.transform.rotation.x = ros_tf.transform.rotation.x
						_f.transform.rotation.y = ros_tf.transform.rotation.y
						_f.transform.rotation.z = ros_tf.transform.rotation.z
						_f.transform.rotation.w = ros_tf.transform.rotation.w

						_f.type = topics_to_save[topic_name][1]

					# Add file to the corresponding stream
					addFileToStream(
					  qs,
					  topics_to_save[topic_name][0],
					  (
					    (timestamp.secs,timestamp.nsecs),
					    filename
					  )
					)

					# Mark the new file as the current one
					current_state[topic_name] = filename

					# Create a frame if several topics are being recorded
					if len(current_state)>1:
						frame = []
						for current_file in current_state.values():
							if current_file is None:
								break
							else:
								frame.append(current_file)
						else:
							qs.createNewFrame(*frame)
					counter[topic_name] += 1

		qs.context = ds_context
		qs.examineContent()
		qs.close()

else:
	def makeQiDataSetFromROSbag(rosbag_path, topic_to_prefix, ds_context):
		raise Exception(
		  "ROS python package were not found. Did you source the environment ?"
		)
