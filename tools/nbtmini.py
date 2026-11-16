"""Minimal NBT reader (no deps): parse(bytes)->python structure. Used for palette surveys."""
import struct
def parse(data):
    pos=[0]
    def r(fmt):
        s=struct.calcsize(fmt); v=struct.unpack_from(fmt,data,pos[0])[0]; pos[0]+=s; return v
    def string():
        n=r('>H'); s=data[pos[0]:pos[0]+n].decode('utf8','replace'); pos[0]+=n; return s
    def payload(t):
        if t==1: return r('>b')
        if t==2: return r('>h')
        if t==3: return r('>i')
        if t==4: return r('>q')
        if t==5: return r('>f')
        if t==6: return r('>d')
        if t==7: n=r('>i'); pos[0]+=n; return None
        if t==8: return string()
        if t==9:
            it=r('>b'); n=r('>i'); return [payload(it) for _ in range(n)]
        if t==10:
            d={}
            while True:
                tt=r('>b')
                if tt==0: return d
                k=string(); d[k]=payload(tt)
        if t==11: n=r('>i'); pos[0]+=4*n; return None
        if t==12: n=r('>i'); pos[0]+=8*n; return None
        raise ValueError(t)
    t=r('>b'); string(); return payload(t)
