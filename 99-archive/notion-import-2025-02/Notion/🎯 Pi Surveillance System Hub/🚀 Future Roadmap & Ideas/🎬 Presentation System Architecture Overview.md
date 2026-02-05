---

---
# **Presentation Outline: Essential Concepts**

## **1. Introduction & Context**

- [x] Define the lab surveillance problem and requirements
- [x] Explain budget constraints compared to commercial NVR systems

## **2. System Architecture Overview**

- [x] Present the two-machine architecture concept
- [x] Explain Raspberry Pi role as dedicated streamer
- [x] Explain Ubuntu Server role as NVR (Frigate)
- [x] Discuss why physical separation matters
- [ ] Describe network design: Fixed IPs, RTSP ports, TCP vs UDP
- [x] Explain PoE+ switch role: Power delivery + data routing
- [x] Discuss Ethernet cable requirements (Cat6, PoE-certified)
- [x] Show complete network topology diagram
- [x] Illustrate data flow: Camera → rpicam-vid → go2rtc → RTSP → Frigate → Storage

## **3. Why Not Commercial Solutions**

- [x] Compare costs with commercial alternatives
- [x] Discuss flexibility limitations of commercial systems
- [x] Address privacy concerns with cloud-based solutions
- [x] Analyze cloud storage cost implications

## **4. Alternative Architectures Evaluated**

- [x] Evaluate USB Camera Systems: bandwidth bottleneck and single point of failure
- [x] Evaluate Raspberry Pi Zero 2 W: heat issues and maintenance complexity
- [x] Evaluate Raspberry Pi 4: single CSI port limitation
- [x] Evaluate All-in-One Pi + Frigate: resource constraints

## **5. Raspberry Pi 5 Deep Dive**

- [x] Present hardware specifications and capabilities
- [x] Explain dual CSI port advantage (5 boards vs 10)
- [x] Discuss PoE+ integration benefits
- [x] Provide cost-benefit analysis versus alternatives

## **6. Camera Hardware**

- [x] Compare camera module options (v2, v3, HQ, Global Shutter)
- [x] Discuss resolution and FPS considerations
- [x] Justify Camera v3 selection

## **7. rpicam-vid**

- [ ] Define rpicam-vid and its purpose
- [ ] Explain hardware encoder access advantages
- [ ] Compare with alternatives (libcamera-vid, ffmpeg, v4l2)
- [ ] Demonstrate command structure and key parameters

## **8. go2rtc: The Streaming Engine**

- [ ] Introduce go2rtc and its role
- [ ] Compare with alternatives (MediaMTX, FFmpeg server, VLC)
- [ ] Explain architecture: rpicam-vid → go2rtc → RTSP
- [ ] Show configuration structure

## **8.5 go2rtc Installation Steps**

- [ ] Download go2rtc binary
- [ ] Install to /usr/local/bin/ or /opt/go2rtc/
- [ ] Set up directory structure
- [ ] Configure file permissions (chown, chmod)
- [ ] Create configuration file location

## **9. Frigate: The NVR**

- [ ] Introduce Frigate NVR system
- [ ] Compare with alternatives (MotionEye, Shinobi, ZoneMinder)
- [ ] Explain Docker deployment benefits
- [ ] Demonstrate manual recording feature
- [ ] Discuss hardware acceleration capabilities
- [ ] Show web interface functionality

## **9.5 Frigate Installation Steps**

- [ ] Install Docker and Docker Compose on Ubuntu Server
- [ ] Create docker-compose.yml file
- [ ] Set up volume mounts for recordings
- [ ] Configure device access (/dev/dri for Intel GPU)
- [ ] Deploy container with docker compose up -d
- [ ] Verify container is running

## **10. The "Golden" Configurations**

- [ ] Show complete go2rtc.yaml with exec command structure
- [ ] Explain: rpicam-vid stdout → go2rtc stdin (direct pipe)
- [ ] Explain H.264 choice: --codec libav --libav-format h264
- [ ] Explain why NOT H.265: Caused kernel panics on Pi 5
- [ ] Explain why NOT TCP streaming architecture: Unstable (versions 1-4 failed)
- [ ] Show complete systemd service file
- [ ] Explain KillMode=control-group: Prevents zombie rpicam-vid processes
- [ ] Explain resource limits: CPUQuota=70%, MemoryMax=512M
- [ ] Show Frigate camera input configuration
- [ ] Explain -rtsp_transport tcp (not UDP)
- [ ] Explain buffering: -buffer_size 512000 -max_delay 500000
- [ ] Explain Intel QSV hardware acceleration: hwaccel_args preset-intel-qsv-h264

## **10.5 Configuration File Locations & Structure**

- [ ] Raspberry Pi: /etc/go2rtc.yaml
- [ ] Raspberry Pi: /etc/systemd/system/go2rtc.service
- [ ] Raspberry Pi: /boot/firmware/config.txt
- [ ] Ubuntu Server: docker-compose.yml location
- [ ] Ubuntu Server: config/config.yml (Frigate config)
- [ ] Show directory structure for both machines

## **11. System Hardening**

- [ ] Explain /boot/firmware/config.txt modifications
- [ ] Configure hardware watchdog
- [ ] Disable WiFi/Bluetooth for stability
- [ ] Set appropriate GPU memory allocation (gpu_mem=128)
- [ ] Configure static IP address (/etc/dhcpcd.conf or netplan)
- [ ] Justify each hardening measure

## **11.5 System Verification & Testing**

- [ ] Test go2rtc web interface ([http://192.168.0.11:1984](http://192.168.0.11:1984/))
- [ ] Verify RTSP streams with ffprobe
- [ ] Check systemd service status
- [ ] Monitor logs: journalctl -u go2rtc -f
- [ ] Test Frigate web interface ([http://192.168.0.50:5000](http://192.168.0.50:5000/))
- [ ] Verify recordings are being saved
- [ ] Check hardware acceleration is working
- [ ] Confirm CPU usage is low with hardware encoding

## **12. Critical Stability Lessons (Iteration History)**

- [ ] Version 1-2: H.265 codec → Kernel panics (abandoned)
- [ ] Version 3: TCP streaming (rpicam-vid → port → go2rtc) → Unstable (abandoned)
- [ ] Version 4: Missing KillMode → Zombie processes froze Pi after 3-4 days
- [ ] Version 4: No resource limits → Memory exhaustion
- [ ] Version 5: exec + libav + KillMode → Stable 30+ days ✓
- [ ] The importance of the iteration process
- [ ] How each failure informed the next version

## **13. Distributed Architecture Advantages**

- [ ] Explain elimination of USB bandwidth bottleneck
- [ ] Demonstrate fault tolerance: isolated node failures
- [ ] Discuss local processing power per node benefits
- [ ] Present hardware-level EEG synchronization capability
- [ ] Compare cabling simplicity: 5 Ethernet vs 20 USB/power cables

## **14. System Reliability**

- [ ] Present uptime metrics and performance data
- [ ] Explain self-healing capabilities
- [ ] Demonstrate resource monitoring approach
- [ ] Describe failure recovery mechanisms

## **15. Data Storage & Management**

- [ ] Storage location on Ubuntu server (/media/frigate)
- [ ] Frigate retention policies (days to keep)
- [ ] Storage requirements: ~16GB per camera per day
- [ ] How to export/download recordings
- [ ] Backup strategy to NAS
- [ ] Disk space monitoring

## **16. Scalability**

- [ ] Document current setup: 5 Pi boards, 10 cameras
- [ ] Explain Ethernet switch capacity: 153W PoE budget
- [ ] Define maximum capacity: 6 Pi boards (12 cameras)
- [ ] Outline expansion strategy for future growth

## **17. Practical Operations**

- [ ] Describe student access and training requirements
- [ ] Demonstrate starting/stopping recordings
- [ ] Show how to access footage
- [ ] Explain system monitoring procedures
- [ ] Outline routine maintenance tasks
- [ ] Common troubleshooting commands
- [ ] How to check if streams are running
- [ ] How to restart services safely
- [ ] Where to check logs

## **18. Future Capabilities**

- [ ] Present on-board real-time video analysis possibilities
- [ ] Discuss AI/ML behavior tracking integration
- [ ] Explain precise EEG-video synchronization potential
- [ ] Propose remote monitoring dashboard development
- [ ] Outline automated analysis pipeline opportunities

## **19. Cost Analysis**

- [ ] Calculate USB Setup costs: ~1,100-1,200K KRW (plus hidden costs)
- [ ] Calculate Pi Zero 2 W costs: ~650K KRW
- [ ] Calculate Pi 5 Setup costs: ~1,380K KRW
- [ ] Calculate Commercial CCTV costs: ~2,600-5,200K KRW
- [ ] Analyze total cost of ownership across solutions

## **20. Lessons Learned**

- [ ] Document what failed in versions 1-4
- [ ] Highlight what worked in version 5
- [ ] Discuss key decisions and trade-offs made
- [ ] Emphasize importance of iteration process
- [ ] Technical debt and future improvements

## **21. Resources & Documentation**

- [ ] Reference Notion workspace documentation
- [ ] Provide access to configuration files
- [ ] Share student onboarding materials
- [ ] GitHub repositories (if any)
- [ ] Community resources and support channels