from flask import jsonify, Response, request
import jwt, functools, sys, hashlib
from keys import keys
import model

#########Decorator for decoding jwt#############
def jwt_required(func):
    @functools.wraps(func)
    def jwt_func():
        if('Authorization' in request.headers.keys()):
            auth=(request.headers['Authorization']).split(' ')
            if(auth[0]=='Bearer'):
                try:
                    payload=jwt.decode(auth[1],keys.jwt_secret)
                    if(model.Organisations.exists(payload['usid'])==404):
                        return (jsonify({'err':'organisation not found'}), 404)
                    else:
                        return func(payload)
                except jwt.exceptions.DecodeError:
                    return (jsonify({'err':'invalid tokken'}), 400)
            else:
                return (jsonify({'err':'Bearer tokken missing'}), 400)
        else:
            return (jsonify({'err':'Bearer tokken missing'}), 400)
    return jwt_func
################################################

def routes(app):
    
    @app.route('/auth/org',methods=['get'])
    @jwt_required
    def orga(payload):
        data=model.Organisations.org(payload['usid'])
        if(data):
            return jsonify({'details':data, 'status':200})
        return jsonify({'err':'Organisation not found', 'status':404})

    @app.route('/auth/requests',methods=['get'])
    @jwt_required
    def reqget(payload):
        data=model.Members.getreq(payload['usid'])
        if(data[1]==404):
            return(jsonify({'err':'No request found under your organisation', 'status':404}), 404)
        return (jsonify({'data':data[0], 'status':200}), 200)

    @app.route('/auth/members',methods=['get'])
    @jwt_required
    def memget(payload):
        data=model.Members.getmem(payload['usid'])
        if(data[1]==404):
            return(jsonify({'err':'No member found under your organisation', 'status':404}), 404)
        return (jsonify({'data':data[0], 'status':200}), 200)

    @app.route('/auth/members',methods=['delete'])
    @jwt_required
    def memdel(payload):
        reg=request.args['reg']
        stat=model.Members.delete(payload['usid'], reg)
        if(stat==404):
            return(jsonify({'err':'No match found for usid', 'status':404}), 404)
        return (jsonify({'result':'deleted', 'status':200}), 200)

    @app.route('/auth/requests',methods=['put'])
    @jwt_required
    def verify(payload):
        reg=request.args['reg']
        stat=model.Members.verify(payload['usid'], reg)
        if(stat==404):
            return(jsonify({'err':'No match found for org and reg', 'status':404}), 404)
        else:
            return (jsonify({'result':'verified', 'status':200}), 200)

    @app.route('/auth/members/download',methods=['get'])
    @jwt_required
    def downloadcsv(payload):
        data=model.Members.csv(payload['usid'])
        resp = Response(data[0])
        resp.headers['Content-Type']="text/csv"
        resp.headers['Content-Disposition']='attachment; filename="'+payload['usid']+'_members.csv"'
        return resp
    
    @app.route('/auth/freemems',methods=['get'])
    @jwt_required
    def freemems(payload):
        start=int(request.args['start'])-8
        end=int(request.args['end'])-8
        day=int(request.args['day'])
        array=[i for i in range(start,end)]
        print(array)
        data=model.Members.freeMem(payload['usid'],day,array)
        if(data): return jsonify({'members':data, 'status':200})
        else: return (jsonify({'err':'No member found', 'status':404}),404)

