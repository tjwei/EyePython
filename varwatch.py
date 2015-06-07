import cgi
try:
    import reprlib #Python 3
except:
    import repr as reprlib # Python2
from IPython.display import Javascript, display, HTML
__ip = None
html_content = """
<style>
table, th, td {
   border: 5px solid black;
} 
#watcher {
    color: #500;
    opacity: 0.7;
    position: fixed;
    height: auto;
    width: 30%;
    right: 0;
    top:0;
    z-index: 1000;
    background: #ccc;
}
</style>
<script>
if($('#watcher').length == 0)
    $( "body" ).append( '<div id="watcher" ></div>')
</script>
"""

def var_str():
    import sys
    ip = __ip
    txt = []
    user_ns = ip.user_ns
    user_ns_hidden = ip.user_ns_hidden
    nonmatching = object()  # This can never be in user_ns
    varnames = [ i for i in user_ns if not i.startswith('_') \
            and (user_ns[i] is not user_ns_hidden.get(i, nonmatching)) ]
    varnames.sort()
    seq_types = ['dict', 'list', 'tuple']
    ndarray_type = None
    if 'numpy' in sys.modules:
        try:
            from numpy import ndarray
        except ImportError:
            pass
        else:
            ndarray_type = ndarray.__name__
    abbrevs = {'IPython.core.macro.Macro' : 'Macro'}
    def type_name(v):
        tn = type(v).__name__
        return abbrevs.get(tn,tn)

    varlist = [ip.user_ns[n] for n in varnames]

    typelist = []
    for vv in varlist:
        tt = type_name(vv)

        if tt=='instance':
            typelist.append( abbrevs.get(str(vv.__class__),
                                         str(vv.__class__)))
        else:
            typelist.append(tt)

    # column labels and # of spaces as separator
    txt.append(['Variable', 'Type', 'Data/Info'])
    # and the table itself
    kb = 1024
    Mb = 1048576  # kb**2
    for vname,var,vtype in zip(varnames,varlist,typelist):
        ent = [vname, vtype] 
        if vtype in seq_types:
            txt.append(ent+[reprlib.repr(var)+" len="+str(len(var))])
        elif vtype == ndarray_type:
            vshape = str(var.shape).replace(',','').replace(' ','x')[1:-1]
            if vtype==ndarray_type:
                # numpy
                vsize  = var.size
                vbytes = vsize*var.itemsize
                vdtype = var.dtype
            vbytes_repr = vbytes
            if vbytes >=100000:    
                if vbytes < Mb:
                    vbytes_repr =  '(%s kb)' % (vbytes/kb,)
                else:
                    vbytes_repr = '(%s Mb)' % (vbytes/Mb,) 
            txt.append(ent+[vbytes_repr])
        else:
            try:
                vstr = str(var)
            except UnicodeEncodeError:
                vstr = unicode_type(var).encode(DEFAULT_ENCODING,
                                           'backslashreplace')
            except:
                vstr = "<object with id %d (str() failed)>" % id(var)
            vstr = vstr.replace('\n', '\\n')
            if len(vstr) < 50:
                txt.append(ent+[vstr])
            else:
                txt.append(ent+[vstr[:25] + "<...>" + vstr[-25:]])
    return txt

def update_watcher(last_vars=dict()):
    vhtml = "<table>"
    var_list = var_str()
    var_changes = dict()
    next_vars = dict()
    
    for tr in var_list:
        next_vars[tr[0]]=(tr[1], tr[2])
        if tr[0] not in last_vars:
            var_changes[tr[0]]=(1,1,1)
        else:
            var_changes[tr[0]]=(0,next_vars[tr[0]][0]!=last_vars[tr[0]][0],next_vars[tr[0]][1]!=last_vars[tr[0]][1])
            
    var_iter = iter(var_list)
    tr = next(var_iter)
    vhtml+= "<tr>"
    for th in tr:
        #style = ""
        style=" style='color: #0f0;background: #555'"
        vhtml+="<th%s>"%style+cgi.escape(str(th))+"</th>"
    vhtml+="</tr>\n"
    for tr in var_iter:
        vhtml+= "<tr>"
        changes = var_changes[tr[0]]
        for i, td in enumerate(tr):
            style = ""
            if changes[i]:
                style=" style='color: #f00;background: #0ff'"
            vhtml+="<td%s>"%style+cgi.escape(str(td))+"</td>"
        vhtml+="</tr>\n"
    vhtml+="</table>"
    display(Javascript("$('#watcher').html(\"%s\")"%vhtml.replace('\n','').replace('"',"")))
    last_vars.clear()
    last_vars.update(next_vars)

def load_ipython_extension(ipython):
    global __ip
    a = reprlib.aRepr
    a.maxdict = a.maxlist = a.maxtuple = a.maxset = a.maxfrozenset = a.maxdeque = a.maxarray = 20
    __ip=ipython
    display(HTML(html_content))
    ipython.events.register('post_execute', update_watcher)