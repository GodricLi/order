# _*_coding:utf-8 _*_
# @Author　 : Ric
from application import db
from common.models.food.Food import Food
from common.models.food.FoodStockChangeLog import FoodStockChangeLog
from common.libs.Helper import get_current_time


class FoodService:
    """美食库存修改日志存入数据库"""

    @staticmethod
    def set_stock_change_log(food_id=0, quantity=0, note=''):
        if food_id < 1:
            return False
        food_info = Food.query.filter_by(id=food_id).first()
        if not food_info:
            return False
        model_stock_change = FoodStockChangeLog()
        model_stock_change.food_id = food_id
        model_stock_change.unit = quantity
        model_stock_change.total_stock = food_info.stock
        model_stock_change.note = note
        model_stock_change.created_time = get_current_time()
        db.session.add(model_stock_change)
        db.session.commit()
        return True
