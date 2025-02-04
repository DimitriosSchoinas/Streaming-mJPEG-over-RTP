# Streaming-mJPEG-over-RTP

In this assignment you will implement a streaming video server and a client that coordinates their
actions through a TCP socket and that exchange data using the Real-time Transfer Protocol (RTP); we
will ignore the possibility of UDP datagram loss.
The application is composed of two processes:
• Server: that stores the video files in its disk and sends their contents in RTP packets
• Client: that will ask for a given file and, in case of success, will receive the RTP packets and
play the file in a window using the TkInter software.
The video to be displayed is composed by a sequence of isolated JPEG Images; this format is close to
MJPEG (Multiple JPEG). The file used to test is called movie.mpeg and is in a proprietary format. It is a
binary file with a sequence of parts, where each part is composed by:
- 5 bytes encoding an integer NB
- The encoding of the JPEG image itself contained in NB bytes
You will implement a streaming video server and a client that coordinates their actions through a TCP
socket and that exchange data using the Real-time Transfer Protocol (RTP); we will ignore the
possibility of UDP datagram loss.


Project PDF:

[Lab08_TPC3.pdf](https://github.com/user-attachments/files/18661018/Lab08_TPC3.pdf)
