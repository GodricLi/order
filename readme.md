Flask订餐系统微信小程序
=====================
##启动
* export ops_config=local|production && python manage.py runserver

##flask-sqlacodegen
    flask-sqlacodegen 'mysql://root:123456@127.0.0.1/food_db' --outfile "common/models/model.py"  --flask
    flask-sqlacodegen 'mysql://root:123456@localhost/food_db' --tables food_cat --outfile "common/models/food/FoodCat.py"  --flask
