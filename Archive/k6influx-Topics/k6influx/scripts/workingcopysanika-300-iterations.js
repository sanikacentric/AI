import { check, sleep } from "k6";
import { Writer, Reader, SchemaRegistry, SCHEMA_TYPE_JSON, SCHEMA_TYPE_STRING, SASL_SCRAM_SHA512, TLS_1_2 } from "k6/x/kafka";
import { Trend, Rate, Counter } from "k6/metrics";
 
export const options = {
  scenarios: {
    sasl_auth: {
      executor: "per-vu-iterations",
      vus: 1,
      maxDuration: "10000s",
      iterations: 300,
      gracefulStop: "1s",
    },
  },
  thresholds: {
    "http_req_duration": ["p(95)<500"], // Example threshold, adjust as needed
  },
  ext: {
    influxdb: {
      // Configure InfluxDB details
      address: 'http://influxdb:8086/', // InfluxDB server address
      database: 'k6', // InfluxDB database name
      username: 'admin',
      password: 'P5IuaJRy04fEQ6sFFiKcRv8fe_veaQFGp3Q3IrjvXhZWckm8JsnPqU6HeOm0KF7OqYJbYrgdw-lidyYCcsRPfw==',
    },
  },
};
 
const brokers = ["b-1.mskqa.cy8z3n.c13.kafka.us-east-1.amazonaws.com:9096", "b-2.mskqa.cy8z3n.c13.kafka.us-east-1.amazonaws.com:9096"];
const topic = "ip.documents";//writer
const consumeTopic = "cds.invoice";//reader
 
const saslConfig = {
  username: "develop",
  password: "z3PhuNGqeh52YpUJcv",
  algorithm: SASL_SCRAM_SHA512,
};
 
const tlsConfig = {
  enableTls: true,
  insecureSkipTlsVerify: true,
  minVersion: TLS_1_2,
};
 
const writer = new Writer({
  brokers: brokers,
  topic: topic,
  sasl: saslConfig,
  tls: tlsConfig,
});
 
const reader = new Reader({
  brokers: brokers,
  topic: consumeTopic,
  sasl: saslConfig,
  tls: tlsConfig,
});
 
const schemaRegistry = new SchemaRegistry();
 
const myTrend = new Trend("my_trend");
const myRate = new Rate("my_rate");
const myCounter = new Counter("my_counter");
 
function generateUUID() {
  // Generate a random UUID (version 4)
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0,
      v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}
 
export default function () {
  const start = Date.now();
 
  let key = schemaRegistry.serialize({
    data: generateUUID(), // Generate a new UUID for the key
    schemaType: SCHEMA_TYPE_STRING,
  });
 
  for (let index = 0; index < 1; index++) {
    const payload = {
      "messageId": generateUUID(),
      "timestamp": Date.now(),
      "eventType": "DocumentCreated",
      "correlationId": generateUUID(),
      "compression": null,
      "ContentType": "json",
      "clientId": "Looktest",
      "version": "1.0",
      "origin": "integration-platform",
      "payload": {
        "transactionId": generateUUID(),
        "documentNumber": `sanikaLoadtest Document to CDS ${generateUUID()}`,
        "supplierId": generateUUID(),
        "buyerId": generateUUID(),
        "s3Bucket": "invoice-data-attach",
        "s3Key": `InvoiceAttachments-Dev/dropoff/${generateUUID()}`,
        "documentType": "invoice",
        "cxml": `<cXML xml:lang='en-US' timestamp='${new Date().toISOString()}' payloadID='${generateUUID()}@prd1246utl2.int.coupa'><Header><From><Credential domain='DUNS'><Identity>Corcentric</Identity></Credential></From><To><Credential domain='NetworkID'><Identity>CLIENT</Identity></Credential></To><Sender><Credential domain='DUNS'><Identity>Corcentric</Identity><SharedSecret>Welcome1</SharedSecret></Credential><UserAgent>PurchaseManager</UserAgent></Sender></Header><Request deploymentMode='production'><InvoiceDetailRequest><InvoiceDetailRequestHeader invoiceID='${generateUUID()}' purpose='standard' operation='new' invoiceDate='${new Date().toISOString()}'><InvoiceDetailHeaderIndicator/><InvoiceDetailLineIndicator/><InvoicePartner><Contact role='billFrom' addressID='CorcProd'><Name xml:lang='en-US'>Pinnacle Fleet Solutions</Name><PostalAddress name='Pinnacle Fleet Solutions'><Street>62861 Collections Center Drive</Street><City>Chicago</City><State>IL </State><PostalCode>60693</PostalCode><Country isoCountryCode='PL'>Poland</Country></PostalAddress></Contact></InvoicePartner><InvoicePartner><Contact role='billTo' addressID='RW132'><Name xml:lang='en-US'>CLIENT National Serv</Name><PostalAddress name='CLIENT National Serv'><Street>P.O. Box # 6700</Street><City>PORTLAND</City><State>OR</State><PostalCode>97228-6700</PostalCode><Country isoCountryCode='US'>United States</Country></PostalAddress></Contact></InvoicePartner><InvoiceDetailShipping><Contact role='shipTo' addressID='RW132'><Name xml:lang='en-US'>Amex Traders</Name><PostalAddress name='Amex Traders'><Street>P.O. Box # 6701</Street><City>MARYLAND</City><State>GA</State><PostalCode>30005</PostalCode><Country isoCountryCode='US'>United States</Country></PostalAddress></Contact><Contact role='shipFrom' addressID='RW132'><Name xml:lang='en-US'>Happy Shipping Co</Name><PostalAddress name='Happy Shipping Co'><Street>P.O. Box # 6702</Street><City>GREENLAND</City><State>CA</State><PostalCode>27801-67879</PostalCode><Country isoCountryCode='PL'>Poland</Country></PostalAddress></Contact></InvoiceDetailShipping><InvoiceDetailPaymentTerm payInNumberOfDays='45' percentageRate='0'/></InvoiceDetailRequestHeader><InvoiceDetailOrder><InvoiceDetailOrderInfo><OrderReference><DocumentReference payloadID='13554341'/></OrderReference></InvoiceDetailOrderInfo><InvoiceDetailItem invoiceLineNumber='1' quantity='1.0000'><UnitOfMeasure>EA</UnitOfMeasure><UnitPrice><Money currency='USD'>249.9900</Money></UnitPrice><InvoiceDetailItemReference lineNumber='2'><ItemID><SupplierPartID>77922</SupplierPartID><SupplierPartAuxiliaryID>XX77922</SupplierPartAuxiliaryID></ItemID><Description xml:lang='en-US'>SOME BIG PART</Description></InvoiceDetailItemReference><SubtotalAmount><Money currency='USD'>249.99</Money></SubtotalAmount></InvoiceDetailItem><InvoiceDetailItem invoiceLineNumber='2' quantity='1.0000'><UnitOfMeasure>EA</UnitOfMeasure><UnitPrice><Money currency='USD'>160.9900</Money></UnitPrice><InvoiceDetailItemReference lineNumber='3'><ItemID><SupplierPartID>77923</SupplierPartID><SupplierPartAuxiliaryID>XX77923</SupplierPartAuxiliaryID></ItemID><Description xml:lang='en-US'>SOME SMALL PART</Description></InvoiceDetailItemReference><SubtotalAmount><Money currency='USD'>160.99</Money></SubtotalAmount></InvoiceDetailItem><InvoiceDetailItem invoiceLineNumber='3' quantity='1.0000'><UnitOfMeasure>EA</UnitOfMeasure><UnitPrice><Money currency='USD'>121.9900</Money></UnitPrice><InvoiceDetailItemReference lineNumber='4'><ItemID><SupplierPartID>77921</SupplierPartID><SupplierPartAuxiliaryID>XXX77921</SupplierPartAuxiliaryID></ItemID><Description xml:lang='en-US'>SOMETHING ELSE</Description></InvoiceDetailItemReference><SubtotalAmount><Money currency='USD'>121.99</Money></SubtotalAmount></InvoiceDetailItem></InvoiceDetailOrder><InvoiceDetailSummary><SubtotalAmount><Money currency='USD'>532.9700</Money></SubtotalAmount><Tax><Money currency='USD'>0.00</Money><Description xml:lang='en-US'>tax</Description><TaxDetail purpose='tax' category='sales'><TaxAmount><Money currency='USD'>0.00</Money></TaxAmount><Description xml:lang='en-US'>tax</Description></TaxDetail></Tax><SpecialHandlingAmount><Money currency='USD'>0.00</Money></SpecialHandlingAmount><ShippingAmount><Money currency='USD'>0.00</Money></ShippingAmount><GrossAmount><Money currency='USD'>532.9700</Money></GrossAmount><InvoiceDetailDiscount><Money currency='USD'>0.00</Money></InvoiceDetailDiscount><NetAmount><Money currency='USD'>532.97</Money></NetAmount><DepositAmount><Money currency='USD'>0.00</Money></DepositAmount><DueAmount><Money currency='USD'>532.97</Money></DueAmount></InvoiceDetailSummary></InvoiceDetailRequest></Request></cXML>`,
        "attachments": [
          {
            "Id": generateUUID(),
            "Url": `s3Url${generateUUID()}`
          },
          {
            "Id": generateUUID(),
            "Url": `s3Url${generateUUID()}`
          }
        ]
      }
    };
 
    console.log("Original payload:", JSON.stringify(payload));
 
    let value = schemaRegistry.serialize({
      data: payload,
      schemaType: SCHEMA_TYPE_JSON,
    });
 
    writer.produce({
      messages: [
        {
          key: key,
          value: value,
        },
      ],
    });
 
    // Debugging deserialization
    const deserializedValue = schemaRegistry.deserialize({
      data: value,
      schemaType: SCHEMA_TYPE_JSON,
    });
 
    //console.log("Deserialized payload:", JSON.stringify(deserializedValue, null, 2));
 
    myTrend.add(1);
    myRate.add(1);
    myCounter.add(1);
  }
 
  sleep(0.02); // Sleep for 3 seconds

  let messages = reader.consume({ limit: 500 });

  sleep(0.02); // Sleep for 3 seconds

  check(messages, {
    "messages returned": (msgs) => msgs.length > 0,
    "key is correct": (msgs) =>
      schemaRegistry
        .deserialize({ data: msgs[0].key, schemaType: SCHEMA_TYPE_STRING })
        .length === 36, // UUID length is 36 characters
    "value is correct": (msgs) =>
      schemaRegistry.deserialize({
        data: msgs[0].value,
        schemaType: SCHEMA_TYPE_JSON,
      }).messageId !== null,
  });


  
  sleep(0.02); // Sleep for 3 seconds
 
  const end = Date.now();
  const diff = end - start;
  console.log(`Test execution time: ${diff} ms`);
}
 
export function teardown(data) {
  writer.close();
  reader.close();
}
 
/*export function handleSummary(data) {
  return {
    "summary_duration": data.metrics.iteration_duration.mean,
    "summary_bandwidth": data.metrics.http_reqs.bytes,
    "summary_requests": data.metrics.http_reqs.count,
  };
 
  console.log('summary_duration:', data.summary_duration);
  console.log('summary_bandwidth:', data.summary_bandwidth);
  console.log('summary_requests:', data.summary_requests);
}*/