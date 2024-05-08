from pexpect import pxssh
s = pxssh.pxssh()
if not s.login ('10.40.228.236', 'nutanix', 'nutanix/4u'):
    print "SSH session failed on login."
    print str(s)
else:
    print "SSH session login successful"
    s.sendline ('ls -l')
    s.prompt()         # match the prompt
    print s.before     # print everything before the prompt.
    s.logout()
