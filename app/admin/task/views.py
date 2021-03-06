# -*- coding:utf-8 -*-
from flask import request, render_template, json
from app import MysqlDB
from .. import admin
from . import models
from . import logic
from ..drive import models as driveModels
from app import common


@admin.route('/task/list', methods=['GET'])
@admin.route('/task/list/')
@common.login_require
def task_list():
    if request.args.get('page'):
        data_list = models.task.all()
        json_data = {"code": 0, "msg": "", "count": 0, "data": []}
        if data_list:
            for result in data_list:
                json_data["count"] = json_data["count"]+1
                if result.status == 0:
                    result.status = "<button class='layui-btn layui-btn-primary layui-btn-xs'>暂停</button>"
                else:
                    result.status = "<button class='layui-btn layui-btn-normal layui-btn-xs'>正常</button>"
                json_data["data"].append(
                    {"id": result.id, "title": result.title, "description": result.description, "command": result.command, "stime": result.stime, "status":result.status, "last_time":str(result.last_time), "update_time":str(result.update_time), "create_time": str(result.create_time)})
        return json.dumps(json_data)
    else:
        return render_template('admin/task/list.html', top_nav='task', activity_nav='list')


@admin.route('/task/task_edit/<int:id>', methods=['GET', 'POST'])
@common.login_require
def task_edit(id):
    if request.method == 'GET':
        if id:
            data_list = models.task.find_by_id(id)
            result = {}
            result["id"] = data_list.id
            result["title"] = data_list.title
            result["description"] = data_list.description
            result["command"] = data_list.command
            result["stime"] = data_list.stime
            result["source"] = data_list.source
            result["status"] = data_list.status
        else:
            result = {
                'id': '0'
                , 'source': 0
                , 'status': 1
            }
        return render_template('admin/task/edit.html', top_nav='task', activity_nav='edit', data=result)
    else:
        id = request.form['id']
        title = request.form['title']
        description = request.form['description']
        command = request.form['command']
        stime = request.form['stime']
        source = request.form['source']
        if 'status' in request.form.keys():
            status = 1
        else:
            status = 0
        if id != '0':
            models.task.update({"id": id, "title": title, "description": description, "command": command, "stime": stime, "source": source, "status": status})
        else:
            # 初始化role 并插入数据库
            role = models.task(title=title, description=description, command=command, stime=stime, source=source, status=status)
            MysqlDB.session.add(role)
            MysqlDB.session.flush()
            MysqlDB.session.commit()
        return json.dumps({"code": 0, "msg": "完成！"})


@admin.route('/task/task_del/<int:id>', methods=['GET', 'POST'])  # 删除
@common.login_require
def task_del(id):
    models.task.deldata(id)
    return json.dumps({"code": 0, "msg": "完成！"})


@admin.route('/task/uploads_list', methods=['GET'])
@admin.route('/task/uploads_list/')
@common.login_require
def uploads_list():
    if request.args.get('page'):
        data_list = models.uploads_list.all()
        json_data = {"code": 0, "msg": "", "count": 0, "data": []}
        if data_list:
            for result in data_list:
                json_data["count"] = json_data["count"]+1
                drive_name = driveModels.drive.find_by_id(result.drive_id).title
                if result.status == "0":
                    istask = logic.isPullUploads(result.id)
                    if istask:
                        result.status = "<button class='layui-btn layui-btn-xs'>进行中</button>"
                    else:
                        result.status = "<button class='layui-btn layui-btn-primary layui-btn-xs'>中断</button>"
                elif result.status == "1":
                    result.status = "<button class='layui-btn layui-btn-normal layui-btn-xs'>完成</button>"
                else:
                    result.status = "进行中"
                json_data["data"].append(
                    {"id": result.id, "drive_name": drive_name, "path": result.path, "file_name":result.file_name, "type": result.type, "status":result.status, "update_time":str(result.update_time), "create_time": str(result.create_time)})
        return json.dumps(json_data)
    else:
        return render_template('admin/task/uploads_list.html', top_nav='task', activity_nav='uploads_list')


@admin.route('/task/uploads_list_del/<int:id>', methods=['GET', 'POST'])  # 删除
@common.login_require
def uploads_list_del(id):
    models.uploads_list.deldata(id)
    return json.dumps({"code": 0, "msg": "完成！"})
