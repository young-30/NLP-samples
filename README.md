# Auto-Pinyin-Correction
Automatically correct misspelled Pinyin words to correct Chinese Pinyin.<br>
为拼写错误的拼音单词自动纠正为正确的中文拼音
## 特点
* 主要使用了新闻语料库
* 对学术名词有较高识别率
## 使用
```python
edit_op = EditDistanc()   # 实例化编辑
final_counter = count1.expand_counter(4)  # 参数4表示这里采用了4-gram语言模型扩充counter
correct_sample1 = mixin('qignhuadaxeu', final_counter, edit_op)
correct_sample2 = mixin('zhesihyiege', final_counter, edit_op)
````
## 案列
 `清华大学`  'qignhuadaxeu' => ['qing', 'hua', 'da', 'xue']    <br>
 `这是一个`  'zhesihyiege'  => ['zhe', 'shi', 'yi', 'ge']   
