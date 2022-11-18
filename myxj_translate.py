import gspread
import os.path
import lxml.etree as ET
from sys import exit

# rootdir = "/Users/sven/mtworkspace/android/BeautyCam"
rootdir = os.getcwd()
if not rootdir.endswith('BeautyCam'):
    print('请将该脚本在项目的同目录下执行')
    exit()

version_code = input("请输入版本号（如：10.5.20）: ")
# version_code = '10.5.40'
credentials = {
   #  谷歌文档的账号信息
}

gc = gspread.service_account_from_dict(credentials)
sht = gc.open_by_url(
    'https://docs.google.com/spreadsheets/d/14iFLk4kvz9xjSZ7HsVPglHpmkHj1ZAlOKk1n1A4nJ0w/edit#gid=1715842766')
worksheet = None
try:
    worksheet = sht.worksheet(version_code)
except Exception:
    print("翻译文档中未找到该版本，请确认!!!")
    exit()
google_row_count = worksheet.row_count

google_doc_en_list = []
google_doc_zh_list = []
google_doc_hk_list = []
google_doc_ko_list = []
google_doc_ja_list = []
google_doc_th_list = []

for index in range(google_row_count):
    title_list = list(worksheet.row_values(index + 1))
    if 'English' in title_list:
        enIndex = title_list.index('English')
        zhIndex = title_list.index('Strings Identifier')
        hkIndex = title_list.index('Chinese Traditional (Taiwan)')
        koIndex = title_list.index('ko')
        jaIndex = title_list.index('ja')
        thIndex = title_list.index('th')
        google_doc_en_list = worksheet.col_values(enIndex + 1)
        google_doc_zh_list = worksheet.col_values(zhIndex + 1)
        google_doc_hk_list = worksheet.col_values(hkIndex + 1)
        google_doc_ko_list = worksheet.col_values(koIndex + 1)
        google_doc_ja_list = worksheet.col_values(jaIndex + 1)
        google_doc_th_list = worksheet.col_values(thIndex + 1)
        break

all_res_value_path_list = []
files = os.listdir(rootdir)
for i, file in enumerate(files):
    res_name = os.path.join(rootdir, file) + '/src/main/res'
    if os.path.exists(res_name):
        res_files = os.listdir(res_name)
        for res_item in res_files:
            if "values" in res_item:
                trans_name_1 = os.path.join(res_name, res_item) + "/app_strings.xml"
                trans_name_2 = os.path.join(res_name, res_item) + "/strings.xml"
                if os.path.isfile(trans_name_1):
                    all_res_value_path_list.append(trans_name_1)
                if os.path.isfile(trans_name_2):
                    all_res_value_path_list.append(trans_name_2)

need_trans_path_name_value_list = []
need_trans_xml_path_list = []
for res_value_path in all_res_value_path_list:
    isEnglish = '/values/' in res_value_path
    if not isEnglish:
        continue

    # 找到"待翻译标记（以下为新增文案）"标签一下的文案,像下面找出test2需要翻译的文案（test2-待翻译的文案1）；
    # <string name="test1">test1</string>
    # <!--待翻译标记（以下为新增文案）-->
    # 	<string name="test2">待翻译的文案1</string>
    tree = ET.parse(res_value_path)
    code_info = tree.docinfo.encoding
    with open(res_value_path, encoding=code_info) as fr:
        source_text = fr.read()
        old_content_split = source_text.split('<!--待翻译标记（以下为新增文案）-->')
        if len(old_content_split) != 2 or "<string name=" not in old_content_split[1]:
            continue

    xml_root = ET.parse(res_value_path).getroot()
    isNeedTrans = False
    isAdd = False
    for child in xml_root:
        iscommentType = type(child.tag) != type('str')
        comment = child.text
        if isNeedTrans and not iscommentType:
            name = child.attrib['name']
            value = child.text
            if isNeedTrans:
                need_trans_path_name_value_list.append(res_value_path + ":" + name + ":" + value)
                if not isAdd:
                    need_trans_xml_path_list.append(res_value_path)
                    isAdd = True
        if iscommentType:
            if '待翻译标记（以下为新增文案）' in comment:
                isNeedTrans = True

zh_google_list = []
en_google_list = []
hk_google_list = []
ko_google_list = []
ja_google_list = []
th_google_list = []
not_in_google_doc_zh_value_list = []
in_google_doc_not_all_lang_list = []
only_one_ang_path_name_value_list = []
cannot_trans_path_name_value_list = []
can_trans_zh_value_list = []


def get_trans_by_index(trans_list, index):
    if index < len(trans_list):
        return trans_list[index]
    else:
        ""


need_trans_path_name_value_list_real = []

for index in range(len(need_trans_path_name_value_list)):
    path_name_value = need_trans_path_name_value_list[index]
    split = path_name_value.split(":")
    path = split[0]
    name = split[1]
    trans_zh = split[2]
    if trans_zh in google_doc_zh_list:
        index_row = google_doc_zh_list.index(trans_zh)
        trans_en = get_trans_by_index(google_doc_en_list, index_row)
        trans_hk = get_trans_by_index(google_doc_hk_list, index_row)
        trans_ko = get_trans_by_index(google_doc_ko_list, index_row)
        trans_ja = get_trans_by_index(google_doc_ja_list, index_row)
        trans_th = get_trans_by_index(google_doc_th_list, index_row)
        un_find_lang = ""
        isOnlyOneLang = False
        if not trans_en or not trans_hk or not trans_ko or not trans_ja or not trans_th:
            un_find_lang += "【"
            if not trans_en:
                un_find_lang += "英"
            if not trans_hk:
                un_find_lang += "繁"
            if not trans_ko:
                un_find_lang += "韩"
            if not trans_ja:
                un_find_lang += "日"
            if not trans_th:
                un_find_lang += "泰"
            un_find_lang += "】"
            if not trans_en and not trans_hk and not trans_ko and not trans_ja and not trans_th:
                only_one_ang_path_name_value_list.append(path_name_value)
                isOnlyOneLang = True
            in_google_doc_not_all_lang_list.append(trans_zh + un_find_lang)
            cannot_trans_path_name_value_list.append(path + ":" + name)
        else:
            can_trans_zh_value_list.append(trans_zh)

        if not isOnlyOneLang:
            if trans_en:
                need_trans_path_name_value_list_real.append(path + ":" + name + ":" + trans_en)
                need_trans_path_name_value_list_real.append(
                    path.replace('/values/', '/values-zh/') + ":" + name + ":" + trans_zh)
            else:
                need_trans_path_name_value_list_real.append(path + ":" + name + ":" + trans_zh)
                need_trans_path_name_value_list_real.append(path + ":" + name + ":" + trans_zh)

            if trans_en and trans_hk:
                need_trans_path_name_value_list_real.append(
                    path.replace('/values/', '/values-zh-rHK/') + ":" + name + ":" + trans_hk)
                need_trans_path_name_value_list_real.append(
                    path.replace('/values/', '/values-zh-rTW/') + ":" + name + ":" + trans_hk)
            if trans_en and trans_ko:
                need_trans_path_name_value_list_real.append(
                    path.replace('/values/', '/values-ko/') + ":" + name + ":" + trans_ko)
            if trans_en and trans_ja:
                need_trans_path_name_value_list_real.append(
                    path.replace('/values/', '/values-ja/') + ":" + name + ":" + trans_ja)
            if trans_en and trans_th:
                need_trans_path_name_value_list_real.append(
                    path.replace('/values/', '/values-th/') + ":" + name + ":" + trans_th)
    else:
        # Google翻译文档中没有找到对应的翻译
        cannot_trans_path_name_value_list.append(path + ":" + name)
        not_in_google_doc_zh_value_list.append(trans_zh)
        only_one_ang_path_name_value_list.append(path_name_value)
        need_trans_path_name_value_list_real.append(path_name_value)

print("⚠️共有" + str(
    len(can_trans_zh_value_list)) + "个匹配成功可完成翻译： " + str(can_trans_zh_value_list))
print("⚠️共有" + str(len(in_google_doc_not_all_lang_list)) + "个文案的多语言不全！！！：" + str(in_google_doc_not_all_lang_list))
print("⚠️共有" + str(len(not_in_google_doc_zh_value_list)) + "个文案没有找到翻译,请联系产品补充翻译文案！！！：" + str(
    not_in_google_doc_zh_value_list))


is_continue = input("检查完成，请确认是否继续（输入y继续；输入f翻译不全文案也合入；其他键退出）: ")

isTransForce = False

if is_continue.lower() == "y":
    isTransForce = False
    need_delete_path_name_value_list = []
    for index in range(len(need_trans_path_name_value_list_real)):
        path_name_value = need_trans_path_name_value_list_real[index]
        path = path_name_value.split(":")[0]
        name = path_name_value.split(":")[1]
        if path + ":" + name in cannot_trans_path_name_value_list:
            need_delete_path_name_value_list.append(path_name_value)
    for item in need_delete_path_name_value_list:
        need_trans_path_name_value_list_real.remove(item)

if is_continue.lower() == "f":
    isTransForce = True
    need_delete_path_name_value_list = []
    for path_name_value in only_one_ang_path_name_value_list:
        path = path_name_value.split(":")[0]
        name = path_name_value.split(":")[1]
        value = path_name_value.split(":")[2]
        if value in not_in_google_doc_zh_value_list:
            need_delete_path_name_value_list.append(path + ":" + name)
    for item in need_delete_path_name_value_list:
        cannot_trans_path_name_value_list.remove(item)

if is_continue.lower() != "y" and is_continue.lower() != "f":
    exit()


def start_trans(trans_xml_path):
    if not os.path.isfile(trans_xml_path):
        return
    tree = ET.parse(trans_xml_path)
    code_info = tree.docinfo.encoding
    trans_xml_root = tree.getroot()
    with open(trans_xml_path, encoding=code_info) as fr:
        source_text = fr.read()
    un_trans_list = []
    is_need_trans = False
    for trans_child in trans_xml_root:
        is_comment_type = type(trans_child.tag) != type('str')
        if is_comment_type and '待翻译标记' in trans_child.text:
            is_need_trans = True
        if is_need_trans:
            # 翻译文档未找到的文案不移除
            try:
                path_name_value_temp = trans_xml_path + ":" + trans_child.attrib[
                    'name']
                if cannot_trans_path_name_value_list and path_name_value_temp in cannot_trans_path_name_value_list:
                    un_trans_list.append(trans_child)
            except:
                continue
                # print("trans_child = " + trans_child.text)

    old_content_split = source_text.split('<!--待翻译标记（以下为新增文案）-->')
    if len(old_content_split) != 2:
        # print(trans_xml_path + '未找到《待翻译标记》请检查！！！')
        return
    old_content = old_content_split[0]
    for index in range(len(need_trans_path_name_value_list_real)):
        path_name_value = need_trans_path_name_value_list_real[index]
        split = path_name_value.split(":")
        path = split[0]
        name = split[1]
        word = split[2]
        # 翻译内容为空的话不插入翻译，不作处理；
        if not word:
            continue
        if path not in trans_xml_path:
            continue
        # 从倒数第二个元素开始插入 倒数第一个注解《待翻译标记》
        if path_name_value in only_one_ang_path_name_value_list and isTransForce:
            old_content += '<string name="' + name + '" translatable="false">' + word + '</string>\n\t'
        else:
            old_content += '<string name="' + name + '">' + word + '</string>\n\t'
    old_content += '<!--待翻译标记（以下为新增文案）-->'
    un_trans_list_num = len(un_trans_list)
    if un_trans_list_num > 0:
        old_content += '\n\t'
    else:
        old_content += '\n'
    for index in range(un_trans_list_num):
        item = un_trans_list[index]
        if index == un_trans_list_num - 1:
            old_content += '<string name="' + item.attrib['name'] + '">' + item.text + '</string>\n'
        else:
            old_content += '<string name="' + item.attrib['name'] + '">' + item.text + '</string>\n\t'
    old_content += '</resources>'
    with open(trans_xml_path, 'w', encoding=code_info) as fw:
        fw.write(old_content)


for need_trans_xml_path in need_trans_xml_path_list:
    start_trans(need_trans_xml_path)
    start_trans(need_trans_xml_path.replace('/values/', '/values-zh/'))
    start_trans(need_trans_xml_path.replace('/values/', '/values-zh-rHK/'))
    start_trans(need_trans_xml_path.replace('/values/', '/values-zh-rTW/'))
    start_trans(need_trans_xml_path.replace('/values/', '/values-ja/'))
    start_trans(need_trans_xml_path.replace('/values/', '/values-ko/'))
    start_trans(need_trans_xml_path.replace('/values/', '/values-th/'))


print("导入完成，快去发起核对项吧~👆👆👆")
