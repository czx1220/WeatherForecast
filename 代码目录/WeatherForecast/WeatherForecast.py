import json
import sys 	
from PyQt5.QtWidgets import QApplication , QMainWindow , QMessageBox, QLabel,QFileDialog,QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5 import QtWidgets, QtGui
from Weather import Ui_Form
import requests
import os
from datetime import datetime
import webbrowser

class MainWindow(QMainWindow ):
	def __init__(self, parent=None):    
		super(MainWindow, self).__init__(parent)
		self.ui = Ui_Form()
		self.ui.setupUi(self)
		self.ui.populate_city_names(self.read_city_names())
		self.populate_date()

		
	def read_city_names(self):
		script_dir = os.path.dirname(os.path.abspath(__file__))
		file_path = os.path.join(script_dir, 'city_names.txt')
		city_file = file_path  # 存储城市名称的txt文件
		with open(city_file, 'r', encoding='utf-8') as file:
			city_names = file.read().splitlines()
		return city_names

	def queryWeather(self):
		cityName = self.ui.weatherComboBox.currentText()
		cityCode = self.transCityName(cityName)

		try:
				rep = requests.get('http://t.weather.itboy.net/api/weather/city/' + cityCode)
				rep.encoding = 'utf-8'
				response_json = rep.json()
				print(response_json)

				# 检查是否返回了错误信息
				if 'code' in response_json:
					error_msg = response_json['msg']
					QMessageBox.critical(self, '错误', error_msg)
					return
				
				elif response_json['status'] == 403:
					error_msg = response_json['message']
					QMessageBox.critical(self, '错误', error_msg)
					return

				## 时间
				# 获取当前时间
				current_time = datetime.now().strftime("%H:%M:%S")  ## 不要微秒
				self.ui.label_time.setText(str(current_time))

				## 高低温
				self.ui.high.setText('## '+ response_json['data']['forecast'][0]['high'])
				self.ui.low.setText('## '+response_json['data']['forecast'][0]['low'])

				## 湿度
				self.ui.label_humid.setText('相对湿度'+ response_json['data']['shidu'])

				## 风向风速
				self.ui.label_wind.setText(response_json['data']['forecast'][0]['fx']+ ' ' + response_json['data']['forecast'][0]['fl'])

				## pm25
				self.ui.label_pm.setText(str(response_json['data']['pm25']))

				## 空气质量
				self.ui.label_quality.setText(response_json['data']['quality'])

				# ## 日期
				# self.ui.date.setText(response_json['data']['forecast'][0]['ymd'])

				## 日期
				forecast_data = response_json['data']['forecast']
				self.ui.date.setText(forecast_data[0]['ymd'])
				self.populate_date_list(forecast_data)

				## 日出日落
				self.ui.label_sunrise.setText('日出： ' + response_json['data']['forecast'][0]['sunrise'])
				self.ui.label_sunset.setText('日落： ' + response_json['data']['forecast'][0]['sunset'])

				## notice
				self.ui.text_notice.setText('**' + response_json['data']['forecast'][0]['notice'] + '**')

				# 天气
				self.ui.weather.setText(response_json['data']['forecast'][0]['type'])
				print(response_json['data']['forecast'][0]['type'])
				self.ui.display_weather_icon(response_json['data']['forecast'][0]['type'])
		
		except requests.exceptions.RequestException as e:
			QMessageBox.critical(self, '错误', str(e))
			return
		
	def transCityName(self,cityName):
		cityCode = None  # 初始化 cityCode 变量
		script_dir = os.path.dirname(os.path.abspath(__file__))
		citycodes_path = os.path.join(script_dir, 'city_codes.json')
		with open(citycodes_path, 'r', encoding='utf-8') as file:
			data = json.load(file)
			for province in data['城市代码']:
				for city in province['市']:
					if city['市名'] == cityName:
						cityCode = city['编码']
						break
				if cityCode:  # 如果找到匹配的城市代码，跳出循环
					break
		return cityCode
	
	def populate_date_list(self, forecast_data):
		dates = [forecast['ymd'] for forecast in forecast_data]
		self.ui.dateComboBox.clear()
		self.ui.dateComboBox.addItems(dates)

	def clearResult(self):
		print('* clearResult  ')

		# 获取窗口中的所有 QLabel 部件
		labels = self.findChildren(QLabel)

		# 遍历并清除每个 QLabel 的文本内容
		for label in labels:
			if label.objectName() != "label":
				label.clear()

	def openWeatherWebsite(self):
		# 打开中国天气网
		webbrowser.open("https://weather.cma.cn/")

	def populate_date(self):
		cityName = self.ui.weatherComboBox.currentText()
		cityCode = self.transCityName(cityName)

		try:
			rep = requests.get('http://t.weather.itboy.net/api/weather/city/' + cityCode)
			rep.encoding = 'utf-8'
			response_json = rep.json()
			print(response_json)

			# 检查是否返回了错误信息
			if 'code' in response_json:
				error_msg = response_json['msg']
				QMessageBox.critical(self, '错误', error_msg)
				return

			elif response_json['status'] == 403:
				error_msg = response_json['message']
				QMessageBox.critical(self, '错误', error_msg)
				return

			forecast_data = response_json['data']['forecast']
			# self.ui.date.setText(forecast_data[0]['ymd'])
			self.populate_date_list(forecast_data)

		except requests.exceptions.RequestException as e:
			QMessageBox.critical(self, '错误', str(e))
			return
		
	def on_dateComboBox_activated(self):
		cityName = self.ui.weatherComboBox.currentText()
		cityCode = self.transCityName(cityName)

		try:
			rep = requests.get('http://t.weather.itboy.net/api/weather/city/' + cityCode)
			rep.encoding = 'utf-8'
			response_json = rep.json()
			print(response_json)

			# 检查是否返回了错误信息
			if 'code' in response_json:
				error_msg = response_json['msg']
				QMessageBox.critical(self, '错误', error_msg)
				return

			elif response_json['status'] == 403:
				error_msg = response_json['message']
				# QMessageBox.critical(self, '错误', error_msg)
				QMessageBox.critical(self, '错误', '无法获取到该城市天气')
				return

			date = self.ui.dateComboBox.currentText()

			forecast_data = response_json['data']['forecast']
			selected_forecast = next((forecast for forecast in forecast_data if forecast['ymd'] == date), None)

			if selected_forecast != None:
				## 时间
				# 获取当前时间
				print("成功输出啦")
				current_time = datetime.now().strftime("%H:%M:%S")  ## 不要微秒
				self.ui.label_time.setText(str(current_time))

				## 高低温
				self.ui.high.setText('## ' + selected_forecast['high'])
				self.ui.low.setText('## ' + selected_forecast['low'])

				## 湿度
				self.ui.label_humid.setText('相对湿度' + response_json['data']['shidu'])

				## 风向风速
				self.ui.label_wind.setText(selected_forecast['fx'] + ' ' + selected_forecast['fl'])

				## pm25
				self.ui.label_pm.setText(str(response_json['data']['pm25']))

				## 空气质量
				self.ui.label_quality.setText(response_json['data']['quality'])

				## 日期
				self.ui.date.setText(selected_forecast['ymd'])

				## 日出日落
				self.ui.label_sunrise.setText('日出： ' + selected_forecast['sunrise'])
				self.ui.label_sunset.setText('日落： ' + selected_forecast['sunset'])

				## notice
				self.ui.text_notice.setText('**' + selected_forecast['notice'] + '**')

				# 天气
				self.ui.weather.setText(selected_forecast['type'])
				print(selected_forecast['type'])
				self.ui.display_weather_icon(selected_forecast['type'])
			else:
				QMessageBox.warning(self, '警告', '未找到选定日期的天气信息')

		except requests.exceptions.RequestException as e:
			QMessageBox.critical(self, '错误', str(e))
			return
	
	def saveWeatherInfo(self):
		# 获取天气信息
		weather_info = {
			'时间': self.ui.label_time.text(),
			'高温': self.ui.high.text().replace('## ', ''),
			'低温': self.ui.low.text().replace('## ', ''),
			'湿度': self.ui.label_humid.text(),
			'风向风速': self.ui.label_wind.text(),
			'PM2.5': self.ui.label_pm.text(),
			'空气质量': self.ui.label_quality.text(),
			'日期': self.ui.date.text(),
			'日出': self.ui.label_sunrise.text().replace('日出： ', ''),
			'日落': self.ui.label_sunset.text().replace('日落： ', ''),
			'注意事项': self.ui.text_notice.text(),
			'天气': self.ui.weather.text()
		}

		# 弹出文件夹选择对话框，获取用户选择的文件夹路径
		folder_dialog = QFileDialog()
		folder_path = folder_dialog.getExistingDirectory(self, "选择保存文件夹")

		if folder_path:
			# 构建文件路径
			current_time = datetime.now().strftime("%Y%m%d%H%M%S")
			file_name = f"weather_{current_time}.json"
			file_path = os.path.join(folder_path, file_name)

			# 将天气信息保存到指定文件路径
			with open(file_path, 'w', encoding='utf-8') as file:
				json.dump(weather_info, file, ensure_ascii=False, indent=4)
			
			QMessageBox.information(self, "保存成功", "天气信息已保存。")
		else:
			QMessageBox.warning(self, "保存失败", "未选择保存文件夹。")

if __name__=="__main__":  
	app = QApplication(sys.argv)  
	win = MainWindow()  

	# 设置窗口图标
	script_dir = os.path.dirname(os.path.abspath(__file__))
	icon = QtGui.QIcon((os.path.join(script_dir, 'pics/icon.png')))  # 替换为您自己的图标文件路径
	win.setWindowIcon(icon)

	win.show()  
	sys.exit(app.exec_())  
