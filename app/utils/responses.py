from flask import jsonify


def ok(data=None, message="OK", status=200):
    return jsonify({"success": True, "message": message, "data": data}), status


def created(data=None, message="Created"):
    return ok(data, message, 201)


def error(message="Error", status=400, errors=None):
    return jsonify({"success": False, "message": message, "errors": errors or {}}), status