package com.tianli.cloud.service.crawler.worker.workers.CHINA_MOBILE.ZHEJIANG.test_parse

import com.alibaba.fastjson.JSON
import com.alibaba.fastjson.JSONArray
import com.alibaba.fastjson.JSONObject
import com.fasterxml.jackson.databind.ObjectMapper
import org.joda.time.LocalDateTime
import org.joda.time.LocalDate
import org.joda.time.format.DateTimeFormat
import org.jsoup.Jsoup
import org.jsoup.nodes.Element
import org.jsoup.select.Elements

import com.tianli.cloud.service.crawler.common.dto.BasicInfo
import com.tianli.cloud.service.crawler.common.dto.BillRecord
import com.tianli.cloud.service.crawler.common.dto.CallRecord
import com.tianli.cloud.service.crawler.common.dto.PayRecord
import com.tianli.cloud.service.crawler.worker.utils.PeriodUtil

import java.io.FileReader;


public class test_parse {

    public static void testcallrecord() {
        String path = System.getProperty("user.dir") + "/server/src/main/java/com/tianli/cloud/" +
                "service/crawler/worker/workers/CHINA_MOBILE/ZHEJIANG/test.txt"
        FileReader reader = new FileReader(path);
        String content = reader.text.replaceAll("&nbsp;", "")

        List<CallRecord> callRecordList = new ArrayList<>()

        Elements elements = Jsoup.parse(content).select("tr[class=content2][align=middle]");
//        System.out.println(elements)
        for (Element element : elements) {
            if (element.childNodeSize() < 10) {
                continue
            }
            CallRecord callRecord = new CallRecord()
//            本机号码
            callRecord.mobile = "18680325804"
//            通话时间
            String callDate = element.select("td:eq(1)").html()
            callRecord.callDate = LocalDateTime.parse(callDate, DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss"))
//            通话时长秒
            String call_long_hour = element.select("td:eq(2)").html()
            callRecord.callDuration = PeriodUtil.parseTimeStringToSeconds(call_long_hour)
//            通话类型
            callRecord.callType = element.select("td:eq(4)").html().contains("主叫") ? 1 : 2;
//            对方号码
            callRecord.otherMobile = element.select("td:eq(5)").html()
//            通话地址
            callRecord.callArea = element.select("td:eq(7)").html()
//            通话费用
            callRecord.callCost = new BigDecimal(element.select("td:eq(12)").html())
            callRecordList.add(callRecord)
        }
        println(callRecordList)
    }

    public static void testbillinfo(){
        String path = System.getProperty("user.dir") + "/server/src/main/java/com/tianli/cloud/" +
                "service/crawler/worker/workers/CHINA_MOBILE/ZHEJIANG/test.txt"
        FileReader reader = new FileReader(path);
        String content = reader.text.replaceAll("&nbsp;", "")
        List<BillRecord> billRecordList = new ArrayList<>()
        Elements elements = Jsoup.parse(content).select("div[class=div3]:has(span:contains(费用和账户信息)) table:eq(0) tr");
        BillRecord billRecord = new BillRecord()

        billRecord.fixedFee = new BigDecimal(elements.select("tr:has(th:contains(套餐及固定费)) td").html())
        billRecord.netFee = new BigDecimal(elements.select("tr:has(th:contains(上网费)) td").html())
        billRecord.voiceFee = new BigDecimal(elements.select("tr:has(th:contains(语音通信费)) td").html())
        billRecord.messageFee = new BigDecimal(elements.select("tr:has(th:contains(短彩信费)) td").html())
        billRecord.businessFee = new BigDecimal(elements.select("tr:has(th:contains(增值业务费)) td").html())
        billRecord.basicpackageFee = new BigDecimal(elements.select("tr:has(th:contains(套餐及固定费)) td").html())
        billRecord.flowFee = new BigDecimal(elements.select("tr:has(th:contains(上网费)) td").html())
        billRecord.otherFee = -(new BigDecimal(elements.select("tr:has(th:contains(优惠费)) td").html()))
        billRecord.totalFee = new BigDecimal(elements.select("tr:has(th:contains(合计)) td").html())

        String month = Jsoup.parse(content).select("tr:has(strong:contains(计费周期)) > td").html().split("月")[0]
        billRecord.date = LocalDateTime.parse(month,DateTimeFormat.forPattern("yyyy年MM"))
        billRecordList.add(billRecord)
        println(billRecordList)

    }

    public static void testpayinfo(){
        String path = System.getProperty("user.dir") + "/server/src/main/java/com/tianli/cloud/" +
                "service/crawler/worker/workers/CHINA_MOBILE/ZHEJIANG/test.txt"
        FileReader reader = new FileReader(path);
        String content = reader.text.replaceAll("&nbsp;", "")
        List<PayRecord> payRecordList = new ArrayList<>()
        Element element = Jsoup.parse(content).select("table:has(th:contains(充值方式)) tr:eq(1)")[0]
        PayRecord payRecord = new PayRecord()
        payRecord.payChannel="在线"
        payRecord.payType = element.select("td:eq(2").html()
        payRecord.payDate = LocalDateTime.parse(element.select("td:eq(0)").html(),DateTimeFormat.forPattern("yyyy-MM-dd HH:mm:ss"));
        payRecord.payFee = new BigDecimal(element.select("td:eq(1)").html())
        payRecordList.add(payRecord)
        println(payRecordList)
    }

    public static void testbisicinfo(){
        String path = System.getProperty("user.dir") + "/server/src/main/java/com/tianli/cloud/" +
                "service/crawler/worker/workers/CHINA_MOBILE/ZHEJIANG/test.txt"
        FileReader reader = new FileReader(path);
        BasicInfo basicInfo = new BasicInfo()
        String content = reader.text.replaceAll("&nbsp;", "")
        JSONObject jsonObject = (JSONObject) JSONObject.parse(content)
        if (jsonObject != null) {
            JSONObject innerJsonObject = jsonObject.getJSONObject("respKtbbinfoqry")
            println(innerJsonObject)
            println()

//            运营商身份证
            basicInfo.cardId = innerJsonObject.get("custCertCode")
//            运营商号码
            basicInfo.mobile = innerJsonObject.get("contBillId")
//            性别
            basicInfo.gender = ""
//            年龄
            basicInfo.age = ""
//            邮箱
            basicInfo.email = ""
            for (JSONObject arrayJsonobject : innerJsonObject.getJSONArray("infos")){
                if(arrayJsonobject.containsKey("address")){
//                    地址
                    basicInfo.address = arrayJsonobject.get("address")
                }
                if(arrayJsonobject.containsKey("list")){
                    String opendate = arrayJsonobject.getJSONArray("list")[0].get("effTime")
//                    开卡时间
                    basicInfo.openDate = LocalDateTime.parse(opendate,DateTimeFormat.forPattern("yyyy年MM月dd日"));
//                    在网时长
                    basicInfo.netAge = (LocalDateTime.now().year-basicInfo.openDate.year-1).toString()
                    List<String> brandName = new ArrayList<String>();
                    List<String> curPlanName = new ArrayList<String>();
                    for(JSONObject innerobject : arrayJsonobject.getJSONArray("list")){
                        brandName.add(innerobject.get("offerName"))
                        curPlanName.add(innerobject.get("offerTypeName"))
                    }
//                    套餐
                    basicInfo.curPlanName = curPlanName.join("^")
//                    品牌
                    basicInfo.brandName = brandName.join("^")
                }

            }
            basicInfo.userStatus = "正常"
            basicInfo.userLevel = innerJsonObject.get("custCertType")
            basicInfo.certification = "实名"
            basicInfo.queryDate = LocalDateTime.now()
        }
        println(basicInfo)

    }

    public static void testStar(){
        String path = System.getProperty("user.dir") + "/server/src/main/java/com/tianli/cloud/" +
                "service/crawler/worker/workers/CHINA_MOBILE/ZHEJIANG/test.txt"
        FileReader reader = new FileReader(path);
        String content = reader.text.replaceAll("&nbsp;", "")
        BigDecimal aa = new BigDecimal(Jsoup.parse(content).select("li[class=mb10] > span").html().replaceAll("余额[:：]|元",""))
        String level = Jsoup.parse(content).select("label[class^=level_show]").html().replaceAll("<.*?>","")
        String sco = Jsoup.parse(content).select("span[class=mr5]:contains(积分)").html().replaceAll("积分\\[|\\]","")
        String name = Jsoup.parse(content).select("span[class^=name]").html()

        println(name)
    }

    public static void main(String[] args) {
//        testcallrecord()
//        testbillinfo()
//        testpayinfo()
        // testStar()
//        testbisicinfo()
    }

}

