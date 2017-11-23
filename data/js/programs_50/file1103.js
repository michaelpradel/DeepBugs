/* This is experimental code made for example and to be taken and customize. 
 * API and implementation of this component can change at anytime, so the best course 
 * is to test it, and make it your own (by change the name space) if you decide to use it.
 */
brite.xp = brite.xp || {};

(function($){
	/**
	 * Create a SQLiteDaoHandler type 
	 * 
	 * @param {String} entityType. create a table for dao with the entity type.
	 * @param {String} tableName. create a table for dao with the tableName.
	 * @param {String} identity. the primary key of the table.
	 * tableDefine. each object for a column in Array, exclude the primary column.
	 * 			Example format:
	 * 			[{column:'name',dtype:'TEXT'},{column:'email',dtype:'TEXT'},{column:'sex',dtype:'INTEGER'}]
	 * 
	 */
	function SQLiteDaoHandler(entityType, tableName, identity){
		this._entityType = entityType;
		this._identity = identity || 'id';
		this._tableName = tableName;
	}

	// --------- DAO Interface Implementation --------- //
	/**
	 * DAO Interface: Return the property ID name
	 * @return the id (this is not deferred), default value is "id"
	 * @throws error if dao cannot be found
	 */
	SQLiteDaoHandler.prototype.getIdName = function(){
		return this._identity || "id";
	}
	
	// --------- DAO Info Methods --------- //
    SQLiteDaoHandler.prototype.entityType = function () {
        return this._entityType;
    };
    // --------- DAO Info Methods --------- //

	
	/**
	 * DAO Interface: Return a deferred object for this id.
	 * @param {Integer} id
	 * @return
	 */
	SQLiteDaoHandler.prototype.get = function(id){
		var dao = this;
		var dfd = $.Deferred();
		if(id){
			var sql = "SELECT * FROM " + dao._tableName + " where "
					+ dao.getIdName() + "=" + id;
			app.SQLiteDB.transaction(function(transaction){
				transaction.executeSql(sql, [], function(transaction, results){
					var row = results.rows.item(0);
					dfd.resolve(row);
				});
			});
		}else{
			dfd.resolve(null);
		}

		return dfd.promise();
	}

	
	/**
	 * DAO Interface: Return a deferred object for this options
	 * @param {Object} opts 
	 *           opts.pageIndex {Number} Index of the page, starting at 0.
	 *           opts.pageSize  {Number} Size of the page
	 *           opts.match     {Object} add condition with expr 'like' in the where clause.
	 *           opts.equal     {Object} add condition with expr '=' in the where clause.
	 *           opts.ids     	{Array}  add condition with expr ' id in (...)' in the where clause.
	 *           opts.orderBy   {String}
	 *           opts.orderType {String} "asc" or "desc"
	 */
	SQLiteDaoHandler.prototype.list = function(opts){
		var dao = this;
		var resultSet;

		var dfd = $.Deferred();
		app.SQLiteDB.transaction(function(transaction){
			var condition = "";
			if(opts){
				if(opts.match){
					var filters = opts.match;
					for(var k in filters){
						condition += " and " + k + " like '%" + filters[k] + "%'";
					}
				}
				
				if(opts.equal){
					var filters = opts.equal;
					for(var k in filters){
						condition += " and " + k + "='" + filters[k] + "'";
					}
				}
				

				if(opts.ids && $.isArray(opts.ids)){
					var ids = opts.ids;
					condition += dao.getIdName() + " and in (";
					for ( var i = 0; i < ids.length; i++) {
						condition += "'" + ids[i] + "'";
						if (i != ids.length - 1) {
							condition += ",";
						}
					}
					condition += ")";
				}
				
				if(opts.orderBy){
					condition += " order by "+ opts.orderBy;
					if(opts.orderType){
						condition += " " + opts.orderType;
					}
				}
				
				if(opts.pageIndex || opts.pageIndex == 0){
					condition += " limit " + (opts.pageIndex * opts.pageSize);
					if(opts.pageSize){
						condition += ","+opts.pageSize;
					}else{
						condition += ", -1";
					}
				}
			}
			
			
			var listSql = "SELECT " + " * " + "FROM " + dao._tableName + " where 1=1 " + condition;
			transaction.executeSql((listSql), [],function(transaction, results){
				dfd.resolve(parseRows2Json(results.rows));
			});

		});
		return dfd.promise();
	}

	
	/**
	 * DAO Interface: Create a new instance of the object for a give  data. <br />
	 *
	 * The DAO resolve with the newly created data.
	 *
	 * @param {Object} data
	 */
	SQLiteDaoHandler.prototype.create = function(data){
		var dao = this;
		var newId;
		var insSql = "INSERT INTO " + dao._tableName + " (";
		var idx = 0;
		var values = "";
		var valus = [];
		for(var k in data){
			if(idx > 0){
				insSql += ",";
				values += ",";
			}
			insSql += k;
			values += "?";
			valus[idx] = data[k];
			idx++;
		}

		insSql += " ) VALUES (" + values + ");";
		var dfd = $.Deferred();
		
		app.SQLiteDB.transaction(function(transaction){
			transaction.executeSql(insSql, valus,function(transaction, results){
				var obj = $.extend({},data);
				obj.id = results.insertId;
				dfd.resolve(obj);
			},function(a,b){
				console.log(b);
			});
		});
		return dfd.promise();
	}

	/**
	 * DAO Interface: update a existing id with a set of property/value data.
	 *
	 * The DAO resolve with the updated data.
	 *
	 * @param {Integer} id
	 * @param {Object} data
	 */
	SQLiteDaoHandler.prototype.update = function(data){
		var dao = this;
		var id = data.id;
		var uptSql = "UPDATE " + dao._tableName + " set ";
		var idx = 0;
		for(var k in data){
			if(idx > 0){
				uptSql += ",";
			}
			uptSql += k + "='" + data[k] + "'";
			idx++;
		}

		uptSql += " where " + dao.getIdName() + "=" + id;
		var dfd = $.Deferred();
		app.SQLiteDB.transaction(function(transaction){
			transaction.executeSql((uptSql), [],function(transaction, results){
				var obj = $.extend({},data);
				obj.id = id;
				dfd.resolve(obj);
			});
		});
		return dfd.promise();
	}

	/**
	 * DAO Interface: remove an instance of objectType for a given  id.
	 *
	 * The DAO resolve with the id.
	 * 
	 * @param {Integer} id
	 * 
	 */
	SQLiteDaoHandler.prototype.remove = function(id){
		var dao = this;
		var dfd = $.Deferred();
		app.SQLiteDB.transaction(function(transaction){

			var delSql = "DELETE FROM " + dao._tableName + " where ";
			var condition = "1 != 1";
			if(id){
				condition = dao.getIdName() + " = '" + id + "'";
			}
			delSql = delSql + condition;
			transaction.executeSql((delSql), [],function(transaction, results){
				dfd.resolve(id);
			});

		});
		return dfd.promise();

	}
	
	// -------- Custom Interface Implementation --------- //
	/**
	 * DAO Interface: remove an instance of objectType for a given ids.
	 *
	 * The DAO resolve with the ids.
	 * 
	 * @param {Array} ids
	 * 
	 */
	SQLiteDaoHandler.prototype.removeAll = function(ids){
		var dao = this;
		var dfd = $.Deferred();
		app.SQLiteDB.transaction(function(transaction){

			var delSql = "DELETE FROM " + dao._tableName + " where ";
			var condition = "1 != 1";
			if(ids){
				condition = dao.getIdName() + " in (";
				for ( var i = 0; i < ids.length; i++) {
					condition += "'" + ids[i] + "'";
					if (i != ids.length - 1) {
						condition += ",";
					}
				}
				condition += ")";
			}
			delSql = delSql + condition;
			transaction.executeSql((delSql), [],function(transaction, results){
				dfd.resolve(ids);
			});

		});
		return dfd.promise();

	}
	
	/**
	 * DAO Interface: Create instances of the object for a give objs. <br />
	 *
	 * The DAO resolve with the newly created data.
	 *
	 * @param {Array} array of data
	 */
	SQLiteDaoHandler.prototype.createAll = function(objs){
		var dao = this;
		var dfd = $.Deferred();
		var returnArray = [];
		app.SQLiteDB.transaction(function(transaction){
			for(var i = 0; i < objs.length; i++){
				
				var data = objs[i];
				var insSql = "INSERT INTO " + dao._tableName + " (";
				var idx = 0;
				var values = "";
				var valuesArray = [];
				for(var k in data){
					if(idx > 0){
						insSql += ",";
						values += ",";
					}
					insSql += k;
					values += "?";
					valuesArray.push(data[k]);
					idx++;
				}

				insSql += " ) VALUES (" + values + ");";
				if(i < objs.length - 1){
					transaction.executeSql(insSql, valuesArray,function(transaction, results){
						var obj = $.extend({},data);
						obj.id = results.insertId;
						returnArray.push(obj);
					});
				}else{
					transaction.executeSql(insSql, valuesArray,function(transaction, results){
						var obj = $.extend({},data);
						obj.id = results.insertId;
						returnArray.push(obj);
						dfd.resolve(returnArray);
					});
				}
			}
			
			
		});
		return dfd.promise();
	}
	
	
	/**
	 * DAO Interface: Return a deferred object for this  options
	 * @param {Object} opts 
	 *           opts.match     {Object} add condition with expr 'like' in the where clause.
	 *           opts.equal     {Object} add condition with expr '=' in the where clause.
	 *           opts.ids     	{Array}  add condition with expr ' id in (...)' in the where clause.
	 */
	SQLiteDaoHandler.prototype.getCount = function(opts){
		var dao = this;
		var resultSet;

		var dfd = $.Deferred();
		app.SQLiteDB.transaction(function(transaction){
			var condition = "";
			if(opts){
				if(opts.match){
					var filters = opts.match;
					for(var k in filters){
						condition += " and " + k + " like '%" + filters[k] + "%'";
					}
				}
				
				if(opts.equal){
					var filters = opts.equal;
					for(var k in filters){
						condition += " and " + k + "='" + filters[k] + "'";
					}
				}
				
				if(opts.ids && $.isArray(opts.ids)){
					var ids = opts.ids;
					condition += dao.getIdName() + " and in (";
					for ( var i = 0; i < ids.length; i++) {
						condition += "'" + ids[i] + "'";
						if (i != ids.length - 1) {
							condition += ",";
						}
					}
					condition += ")";
				}
				
			}
			
			
			var listSql = "SELECT " + "count(*) as 'count' " + "FROM " + dao._tableName + " where 1=1 " + condition;
			transaction.executeSql((listSql), [],function(transaction, results){
				dfd.resolve(results.rows.item(0).count);
			});

		});
		return dfd.promise();
	}
	
	// -------- /Custom Interface Implementation --------- //
	
	// --------- /DAO Interface Implementation --------- //
	brite.xp.SQLiteDaoHandler = SQLiteDaoHandler;

	function parseRows2Json(rows){
		var json = [];
		var rlen = rows.length;
		for(var i = 0; i < rlen; i++){
			json.push(rows.item(i));
		}
		return json;
	}
})(jQuery);