export type Locale = "en" | "ar" | "am";
export interface Translations {
  // App
  appTitle: string;
  searchItem: string;
  // Cart table
  orderSummary: string;
  itemName: string;
  quantity: string;
  price: string;
  total: string;
  subtotal: string;
  vat: string;
  vatPercent: string;
  grandTotal: string;
  submitOrder: string;
  submitNPrintOrder: string;
  invoiceCreated: string;
  barcode: string;
  processingOrder: string;
  youAreOffline: string;
  recheckConnection: string;
  refreshPage: string;
  // Payment
  paymentMethod: string;
  cash: string;
  card: string;
  selectPaymentMethod: string;
  paymentModalSubtitle: string;
  changePaymentMethod: string;
  // Validation
  validationEmptyCart: string;
  validationInvalidQty: (names: string) => string;
  // Aria labels
  ariaQuantity: string;
  ariaUnitPrice: string;
  ariaRemoveItem: (name: string) => string;
  ariaPaymentMethod: string;
  // Currency / units
  currency: string;
  // Misc
  per: string;
  ok: string;
  print: string;
  cancel: string;
  loadingItems: string,
  itemsLoadError: string,
  noResults: string,
  // Tabs
  tabWalkIn: string;
  tabB2B: string;
  // Customer search / create
  searchCustomer: string;
  loadingCustomers: string;
  customersLoadError: string;
  noCustomerResults: string;
  createNewCustomer: string;
  newCustomerName: string;
  newCustomerTaxRegNo: string;
  newCustomerTaxRegNoOptional: string;
  createCustomer: string;
  creatingCustomer: string;
  cancelCreateCustomer: string;
  customerCreateError: string;
  customerNameRequired: string;
  changeCustomer: string;
  noCustomerSelected: string;
  // B2B invoice flow
  createDraftInvoice: string;
  creatingDraftInvoice: string;
  draftInvoiceCreated: string;
  sendInvoice: string;
  sendingInvoice: string;
  invoiceSent: string;
  invoiceStatusDraft: string;
  invoiceStatusSent: string;
  validationNoCustomer: string;
  newInvoice: string;
  // B2B invoice confirmation
  confirmInvoiceBtn: string;
  confirmAndPrintInvoiceBtn: string;
  confirmInvoiceTitle: string;
  confirmInvoiceWarning: string;
  creatingConfirmedInvoice: string;
  noticeInvoiceCreated: string;
  // B2B customer/line-item completeness validation
  customerInfoLoading: string;
  customerInfoComplete: string;
  customerInfoIncomplete: string;
  customerIssueNotVatRegistered: string;
  customerIssueMissingVat: string;
  customerIssueMissingCrn: string;
  customerIssueMissingAddress: string;
  lineItemIssueMissingRate: string;
  lineItemIssueMissingNameEn: string;
  lineItemIssueMissingNameAr: string;
  lineItemIssueMissingDescription: string;
  validationCustomerIncomplete: string;
  validationLineItemsIncomplete: string;
  // Recent Invoices tab
  tabRecentInvoices: string;
  invoiceNumberCol: string;
  dateCol: string;
  typeCol: string;
  customerCol: string;
  statusCol: string;
  typeWalkIn: string;
  typeB2B: string;
  statusPaid: string;
  statusPrinted: string;
  statusDraft: string;
  statusSent: string;
  todaysInvoicesCount: (count: number) => string;
  todaysInvoicesTotal: string;
  loadingInvoices: string;
  invoicesLoadError: string;
  noInvoicesToday: string;
  // Search placeholders (spec §5.2 / §5.3)
  itemSearchPlaceholder: string;
  customerSearchPlaceholder: string;
  addCustomerBtn: string;
  emptyCartMessage: string;
  // Notices (spec §9)
  noticeSubmitted: string;
  noticeSubmittedAndPrinted: string;
  noticeDraftCreated: string;
  noticeInvoiceSent: string;
  // Table column headers (spec §6, values include "(SAR)" per spec)
  unitCol: string;
  priceCol: string;
  lineTotalCol: string;
  // Create-customer modal
  createCustomerTitle: string;
  primaryLangSection: string;
  secondaryLangSection: string;
  identificationSection: string;
  addressSection: string;
  fieldNameAr: string;
  fieldNameEn: string;
  fieldPhone: string;
  fieldVat: string;
  fieldVatOptional: string;
  fieldBuyerIdLabel: string;
  fieldBuyerIdValue: string;
  fieldBuildingNumber: string;
  fieldStreet: string;
  fieldAdditionalNumber: string;
  fieldDistrict: string;
  fieldCity: string;
  fieldState: string;
  fieldPostalCode: string;
  fieldCountry: string;
  scanDocumentBtn: string;
  scanningDocument: string;
  scanDocumentError: string;
  scanDocumentSuccess: string;
  modalSave: string;
  modalSaving: string;
  modalCancel: string;
  buyerIdLabelNone: string;
  requiredFieldsMissing: string;
  vatInvalid: string;
  crnInvalid: string;
}
const en: Translations = {
  appTitle: "New Invoice",
  searchItem: "Search Item",
  orderSummary: "Order Summary",
  itemName: "Item",
  quantity: "Qty",
  price: "Price",
  total: "Total",
  subtotal: "Subtotal (SAR)",
  vat: "VAT",
  vatPercent: "VAT 15% (SAR)",
  grandTotal: "Total (SAR)",
  submitOrder: "Submit",
  submitNPrintOrder: "Print and Submit",
  invoiceCreated: "Invoice created with ID:",
  barcode: "Barcode",
  processingOrder: "Processing order...",
  youAreOffline: "You're offline",
  recheckConnection: "Check your connection and try again.",
  refreshPage: "Refresh page",
  paymentMethod: "Payment Method",
  cash: "Cash",
  card: "Card",
  selectPaymentMethod: "Choose payment method",
  paymentModalSubtitle: "Select how the customer will pay.",
  changePaymentMethod: "Change",
  validationEmptyCart: "Cart is empty. Add at least one item before submitting.",
  validationInvalidQty: (names) => `Quantity must be at least 0.01 for: ${names}`,
  ariaQuantity: "Quantity",
  ariaUnitPrice: "Unit price",
  ariaRemoveItem: (name) => `Remove ${name} from cart`,
  ariaPaymentMethod: "Payment method",
  currency: "SAR",
  per: "/",
  ok: "OK",
  print: "Print",
  cancel: "Cancel",
  loadingItems: "Loading items…",
  itemsLoadError: "Failed to load items. Please refresh.",
  noResults: "No results found",
  tabWalkIn: "Walk-in",
  tabB2B: "B2B Customer",
  searchCustomer: "Search Customer",
  loadingCustomers: "Loading customers…",
  customersLoadError: "Failed to load customers.",
  noCustomerResults: "No customers found",
  createNewCustomer: "+ Create new customer",
  newCustomerName: "Customer name",
  newCustomerTaxRegNo: "VAT registration number",
  newCustomerTaxRegNoOptional: "VAT registration number (optional)",
  createCustomer: "Create customer",
  creatingCustomer: "Creating…",
  cancelCreateCustomer: "Cancel",
  customerCreateError: "Failed to create customer. Please try again.",
  customerNameRequired: "Customer name is required.",
  changeCustomer: "Change",
  noCustomerSelected: "No customer selected",
  createDraftInvoice: "Create Draft Invoice",
  creatingDraftInvoice: "Creating draft…",
  draftInvoiceCreated: "Draft invoice created:",
  sendInvoice: "Send Invoice",
  sendingInvoice: "Sending…",
  invoiceSent: "Invoice sent",
  invoiceStatusDraft: "Draft — not yet sent",
  invoiceStatusSent: "Sent",
  validationNoCustomer: "Select a customer before creating the invoice.",
  newInvoice: "New Invoice",
  confirmInvoiceBtn: "Confirm",
  confirmAndPrintInvoiceBtn: "Confirm & Print",
  confirmInvoiceTitle: "Confirm invoice — this cannot be undone",
  confirmInvoiceWarning: "Once confirmed, this invoice will be created and sent immediately. It cannot be reverted back to a draft or edited afterward. Please make sure everything is correct before continuing.",
  creatingConfirmedInvoice: "Creating invoice…",
  noticeInvoiceCreated: "Invoice created and sent.",
  customerInfoLoading: "Checking customer information…",
  customerInfoComplete: "Customer information is complete.",
  customerInfoIncomplete: "Customer information is incomplete:",
  customerIssueNotVatRegistered: "Customer is not marked as VAT-registered.",
  customerIssueMissingVat: "Missing or invalid VAT registration number.",
  customerIssueMissingCrn: "Missing or invalid CRN (Commercial Registration Number).",
  customerIssueMissingAddress: "Missing or incomplete national address.",
  lineItemIssueMissingRate: "Missing price",
  lineItemIssueMissingNameEn: "Missing English name",
  lineItemIssueMissingNameAr: "Missing Arabic name",
  lineItemIssueMissingDescription: "Missing description",
  validationCustomerIncomplete: "The selected customer's information is incomplete. A B2B invoice cannot be created until it is fixed.",
  validationLineItemsIncomplete: "One or more items are missing required information for a VAT invoice.",
  tabRecentInvoices: "Recent Invoices",
  invoiceNumberCol: "Invoice #",
  dateCol: "Date",
  typeCol: "Type",
  customerCol: "Customer",
  statusCol: "Status",
  typeWalkIn: "Walk-In",
  typeB2B: "B2B",
  statusPaid: "Paid",
  statusPrinted: "Printed",
  statusDraft: "Draft",
  statusSent: "Sent",
  todaysInvoicesCount: (count) => `${count} invoice${count === 1 ? "" : "s"} today`,
  todaysInvoicesTotal: "Total (SAR)",
  loadingInvoices: "Loading invoices…",
  invoicesLoadError: "Failed to load invoices.",
  noInvoicesToday: "No invoices yet today.",
  itemSearchPlaceholder: "Scan or search item by name / SKU...",
  customerSearchPlaceholder: "Search B2B customer by name or city...",
  addCustomerBtn: "Add Customer",
  emptyCartMessage: "No items added yet. Search above to add items.",
  noticeSubmitted: "Invoice submitted.",
  noticeSubmittedAndPrinted: "Invoice submitted and sent to printer.",
  noticeDraftCreated: "Draft invoice created.",
  noticeInvoiceSent: "Invoice sent.",
  unitCol: "Unit",
  priceCol: "Price (SAR)",
  lineTotalCol: "Line Total",
  createCustomerTitle: "Create Customer",
  primaryLangSection: "Primary (Arabic)",
  secondaryLangSection: "Secondary (English)",
  identificationSection: "Identification",
  addressSection: "Address",
  fieldNameAr: "Name (Arabic)",
  fieldNameEn: "Name (English)",
  fieldPhone: "Phone",
  fieldVat: "VAT registration number",
  fieldVatOptional: "VAT registration number (optional)",
  fieldBuyerIdLabel: "ID type",
  fieldBuyerIdValue: "CRN (Commercial Registration Number)",
  fieldBuildingNumber: "Building number",
  fieldStreet: "Street",
  fieldAdditionalNumber: "Additional number",
  fieldDistrict: "District",
  fieldCity: "City",
  fieldState: "State / Region",
  fieldPostalCode: "Postal code",
  fieldCountry: "Country",
  scanDocumentBtn: "Scan document (AI)",
  scanningDocument: "Scanning document…",
  scanDocumentError: "Couldn't read that document. Please fill the form manually.",
  scanDocumentSuccess: "Fields filled from document — please review before saving.",
  modalSave: "Save Customer",
  modalSaving: "Saving…",
  modalCancel: "Cancel",
  buyerIdLabelNone: "None",
  requiredFieldsMissing: "Please fill in all required fields.",
  vatInvalid: "Invalid VAT number — must be 15 digits, starting and ending with 3.",
  crnInvalid: "Invalid CRN — must be 10 digits, starting with 1 or 7.",
};
const ar: Translations = {
  appTitle: "فاتورة جديدة",
  searchItem: "ابحث عن صنف",
  orderSummary: "ملخص الطلب",
  itemName: "اسم الصنف",
  quantity: "الكمية",
  price: "السعر",
  total: "الإجمالي",
  subtotal: "المجموع الفرعي (ريال)",
  vat: "ضريبة القيمة المضافة",
  vatPercent: "ضريبة القيمة المضافة ١٥٪ (ريال)",
  grandTotal: "الإجمالي (ريال)",
  submitOrder: "تأكيد",
  submitNPrintOrder: "تأكيد وطباعة",
  invoiceCreated: "تم إنشاء الفاتورة بالرقم:",
  barcode: "الباركود",
  processingOrder: "جاري معالجة الطلب...",
  youAreOffline: "أنت غير متصل بالشبكة",
  recheckConnection: "تحقق من اتصالك وحاول مرة أخرى.",
  refreshPage: "تحديث الصفحة",
  paymentMethod: "طريقة الدفع",
  cash: "نقداً",
  card: "بطاقة",
  selectPaymentMethod: "اختر طريقة الدفع",
  paymentModalSubtitle: "حدد طريقة دفع العميل.",
  changePaymentMethod: "تغيير",
  validationEmptyCart: "السلة فارغة. أضف صنفاً واحداً على الأقل قبل التأكيد.",
  validationInvalidQty: (names) => `يجب أن تكون الكمية 0.01 على الأقل للأصناف التالية: ${names}`,
  ariaQuantity: "الكمية",
  ariaUnitPrice: "سعر الوحدة",
  ariaRemoveItem: (name) => `إزالة ${name} من السلة`,
  ariaPaymentMethod: "طريقة الدفع",
  currency: "SAR",
  per: "/",
  ok: "OK",
  print: "Print",
  cancel: "إلغاء",
  loadingItems: "جارٍ تحميل العناصر…",
  itemsLoadError: "فشل تحميل العناصر. يرجى التحديث.",
  noResults: "لا توجد نتائج",
  tabWalkIn: "زبون مباشر",
  tabB2B: "عميل تجاري",
  searchCustomer: "ابحث عن عميل",
  loadingCustomers: "جارٍ تحميل العملاء…",
  customersLoadError: "فشل تحميل العملاء.",
  noCustomerResults: "لا يوجد عملاء",
  createNewCustomer: "+ إنشاء عميل جديد",
  newCustomerName: "اسم العميل",
  newCustomerTaxRegNo: "الرقم الضريبي",
  newCustomerTaxRegNoOptional: "الرقم الضريبي (اختياري)",
  createCustomer: "إنشاء العميل",
  creatingCustomer: "جارٍ الإنشاء…",
  cancelCreateCustomer: "إلغاء",
  customerCreateError: "فشل إنشاء العميل. يرجى المحاولة مرة أخرى.",
  customerNameRequired: "اسم العميل مطلوب.",
  changeCustomer: "تغيير",
  noCustomerSelected: "لم يتم اختيار عميل",
  createDraftInvoice: "إنشاء فاتورة كمسودة",
  creatingDraftInvoice: "جارٍ إنشاء المسودة…",
  draftInvoiceCreated: "تم إنشاء مسودة الفاتورة:",
  sendInvoice: "إرسال الفاتورة",
  sendingInvoice: "جارٍ الإرسال…",
  invoiceSent: "تم إرسال الفاتورة",
  invoiceStatusDraft: "مسودة — لم يتم الإرسال بعد",
  invoiceStatusSent: "تم الإرسال",
  validationNoCustomer: "اختر عميلاً قبل إنشاء الفاتورة.",
  newInvoice: "فاتورة جديدة",
  confirmInvoiceBtn: "تأكيد",
  confirmAndPrintInvoiceBtn: "تأكيد وطباعة",
  confirmInvoiceTitle: "تأكيد الفاتورة — لا يمكن التراجع عن هذا الإجراء",
  confirmInvoiceWarning: "بمجرد التأكيد، سيتم إنشاء الفاتورة وإرسالها فوراً. لا يمكن إعادتها إلى مسودة أو تعديلها بعد ذلك. يرجى التأكد من صحة جميع البيانات قبل المتابعة.",
  creatingConfirmedInvoice: "جارٍ إنشاء الفاتورة…",
  noticeInvoiceCreated: "تم إنشاء الفاتورة وإرسالها.",
  customerInfoLoading: "جارٍ التحقق من بيانات العميل…",
  customerInfoComplete: "بيانات العميل مكتملة.",
  customerInfoIncomplete: "بيانات العميل غير مكتملة:",
  customerIssueNotVatRegistered: "العميل غير مسجل في ضريبة القيمة المضافة.",
  customerIssueMissingVat: "الرقم الضريبي مفقود أو غير صحيح.",
  customerIssueMissingCrn: "رقم السجل التجاري (CRN) مفقود أو غير صحيح.",
  customerIssueMissingAddress: "العنوان الوطني مفقود أو غير مكتمل.",
  lineItemIssueMissingRate: "السعر مفقود",
  lineItemIssueMissingNameEn: "الاسم الإنجليزي مفقود",
  lineItemIssueMissingNameAr: "الاسم العربي مفقود",
  lineItemIssueMissingDescription: "الوصف مفقود",
  validationCustomerIncomplete: "بيانات العميل المحدد غير مكتملة. لا يمكن إنشاء فاتورة B2B حتى يتم إصلاحها.",
  validationLineItemsIncomplete: "صنف واحد أو أكثر يفتقر إلى معلومات مطلوبة لفاتورة ضريبية.",
  tabRecentInvoices: "الفواتير الأخيرة",
  invoiceNumberCol: "رقم الفاتورة",
  dateCol: "التاريخ",
  typeCol: "النوع",
  customerCol: "العميل",
  statusCol: "الحالة",
  typeWalkIn: "زبون مباشر",
  typeB2B: "عميل تجاري",
  statusPaid: "مدفوعة",
  statusPrinted: "مطبوعة",
  statusDraft: "مسودة",
  statusSent: "مرسلة",
  todaysInvoicesCount: (count) => `${count} فاتورة اليوم`,
  todaysInvoicesTotal: "الإجمالي (ريال)",
  loadingInvoices: "جارٍ تحميل الفواتير…",
  invoicesLoadError: "فشل تحميل الفواتير.",
  noInvoicesToday: "لا توجد فواتير اليوم بعد.",
  itemSearchPlaceholder: "امسح أو ابحث عن الصنف بالاسم / الرمز...",
  customerSearchPlaceholder: "ابحث عن عميل تجاري بالاسم أو المدينة...",
  addCustomerBtn: "إضافة عميل",
  emptyCartMessage: "لم تتم إضافة أصناف بعد. ابحث أعلاه لإضافة الأصناف.",
  noticeSubmitted: "تم تأكيد الفاتورة.",
  noticeSubmittedAndPrinted: "تم تأكيد الفاتورة وإرسالها للطباعة.",
  noticeDraftCreated: "تم إنشاء مسودة الفاتورة.",
  noticeInvoiceSent: "تم إرسال الفاتورة.",
  unitCol: "الوحدة",
  priceCol: "السعر (ريال)",
  lineTotalCol: "الإجمالي",
  createCustomerTitle: "إنشاء عميل",
  primaryLangSection: "الأساسي (عربي)",
  secondaryLangSection: "الثانوي (إنجليزي)",
  identificationSection: "بيانات التعريف",
  addressSection: "العنوان",
  fieldNameAr: "الاسم (عربي)",
  fieldNameEn: "الاسم (إنجليزي)",
  fieldPhone: "رقم الهاتف",
  fieldVat: "الرقم الضريبي",
  fieldVatOptional: "الرقم الضريبي (اختياري)",
  fieldBuyerIdLabel: "نوع الهوية",
  fieldBuyerIdValue: "رقم السجل التجاري (CRN)",
  fieldBuildingNumber: "رقم المبنى",
  fieldStreet: "الشارع",
  fieldAdditionalNumber: "الرقم الإضافي",
  fieldDistrict: "الحي",
  fieldCity: "المدينة",
  fieldState: "المنطقة",
  fieldPostalCode: "الرمز البريدي",
  fieldCountry: "الدولة",
  scanDocumentBtn: "مسح المستند (AI)",
  scanningDocument: "جارٍ مسح المستند…",
  scanDocumentError: "تعذّرت قراءة المستند. يرجى تعبئة النموذج يدوياً.",
  scanDocumentSuccess: "تم تعبئة الحقول من المستند — يرجى المراجعة قبل الحفظ.",
  modalSave: "حفظ العميل",
  modalSaving: "جارٍ الحفظ…",
  modalCancel: "إلغاء",
  buyerIdLabelNone: "بلا",
  requiredFieldsMissing: "يرجى تعبئة جميع الحقول المطلوبة.",
  vatInvalid: "الرقم الضريبي غير صحيح — يجب أن يتكون من 15 رقماً ويبدأ وينتهي بالرقم 3.",
  crnInvalid: "رقم السجل التجاري غير صحيح — يجب أن يتكون من 10 أرقام ويبدأ بـ 1 أو 7.",
};
const am: Translations = {
  appTitle: "አዲስ ፋክቱራ",
  searchItem: "ዕቃ ፈልግ",
  orderSummary: "የትዕዛዝ ማጠቃለያ",
  itemName: "የዕቃ ስም",
  quantity: "ብዛት",
  price: "ዋጋ",
  total: "ድምር",
  subtotal: "ንዑስ ድምር (SAR)",
  vat: "VAT",
  vatPercent: "ተ.እ.ታ 15% (SAR)",
  grandTotal: "ጠቅላላ ድምር (SAR)",
  submitOrder: "አስገባ",
  submitNPrintOrder: "አስገባ እና ፐሪንት አርግ",
  invoiceCreated: "የክፍያ ማስታወቂያ በመለያ ተፈጥሯል:",
  barcode: "ባርኮድ",
  processingOrder: "ትዕዛዝ በሂደት ላይ ነው...",
  youAreOffline: "በመስመር ላይ አይደሉም",
  recheckConnection: "እባክዎ ግንኙነትዎን ያረጋግጡ እና ደግመው ይሞክሩ.",
  refreshPage: "እንደገና ይሞክሩ",
  paymentMethod: "የክፍያ ዘዴ",
  cash: "ጥሬ ገንዘብ",
  card: "ካርድ",
  selectPaymentMethod: "የክፍያ ዘዴ ይምረጡ",
  paymentModalSubtitle: "ደንበኛው እንዴት እንደሚከፍል ይምረጡ።",
  changePaymentMethod: "ለውጥ",
  validationEmptyCart: "ጋሪው ባዶ ነው። ከማስገባትዎ በፊት ቢያንስ አንድ ዕቃ ይጨምሩ።",
  validationInvalidQty: (names) => `ለሚከተሉት ዕቃዎች ብዛት ቢያንስ 0.01 መሆን አለበት፦ ${names}`,
  ariaQuantity: "ብዛት",
  ariaUnitPrice: "የአንድ ክፍል ዋጋ",
  ariaRemoveItem: (name) => `${name} ከጋሪ አውጣ`,
  ariaPaymentMethod: "የክፍያ ዘዴ",
  currency: "SAR",
  per: "/",
  ok: "እሺ",
  print: "ፕሪንት",
  cancel: "ተወው",
  loadingItems: "እቃዎች እየተጫኑ ነው…",
  itemsLoadError: "እቃዎችን መጫን አልተሳካም። እባክዎ ያድስ።",
  noResults: "ምንም ውጤት አልተገኘም",
  tabWalkIn: "ቀጥታ ደንበኛ",
  tabB2B: "የንግድ ደንበኛ",
  searchCustomer: "ደንበኛ ፈልግ",
  loadingCustomers: "ደንበኞች እየተጫኑ ነው…",
  customersLoadError: "ደንበኞችን መጫን አልተሳካም።",
  noCustomerResults: "ምንም ደንበኛ አልተገኘም",
  createNewCustomer: "+ አዲስ ደንበኛ ፍጠር",
  newCustomerName: "የደንበኛ ስም",
  newCustomerTaxRegNo: "የግብር ምዝገባ ቁጥር",
  newCustomerTaxRegNoOptional: "የግብር ምዝገባ ቁጥር (አማራጭ)",
  createCustomer: "ደንበኛ ፍጠር",
  creatingCustomer: "እየተፈጠረ ነው…",
  cancelCreateCustomer: "ተወው",
  customerCreateError: "ደንበኛ መፍጠር አልተሳካም። እባክዎ እንደገና ይሞክሩ።",
  customerNameRequired: "የደንበኛ ስም ያስፈልጋል።",
  changeCustomer: "ለውጥ",
  noCustomerSelected: "ምንም ደንበኛ አልተመረጠም",
  createDraftInvoice: "የደረቅ ፋክቱራ ፍጠር",
  creatingDraftInvoice: "ደረቅ ፋክቱራ እየተፈጠረ ነው…",
  draftInvoiceCreated: "ደረቅ ፋክቱራ ተፈጥሯል:",
  sendInvoice: "ፋክቱራ ላክ",
  sendingInvoice: "እየተላከ ነው…",
  invoiceSent: "ፋክቱራው ተልኳል",
  invoiceStatusDraft: "ደረቅ — እስካሁን አልተላከም",
  invoiceStatusSent: "ተልኳል",
  validationNoCustomer: "ፋክቱራ ከመፍጠርዎ በፊት ደንበኛ ይምረጡ።",
  newInvoice: "አዲስ ፋክቱራ",
  confirmInvoiceBtn: "አረጋግጥ",
  confirmAndPrintInvoiceBtn: "አረጋግጥ እና አትም",
  confirmInvoiceTitle: "ፋክቱራ አረጋግጥ — ይህ ሊቀለበስ አይችልም",
  confirmInvoiceWarning: "ከተረጋገጠ በኋላ፣ ይህ ፋክቱራ ወዲያውኑ ይፈጠራል እና ይላካል። ወደ ደረቅ መመለስ ወይም በኋላ ማስተካከል አይቻልም። እባክዎ ከመቀጠልዎ በፊት ሁሉም ነገር ትክክል መሆኑን ያረጋግጡ።",
  creatingConfirmedInvoice: "ፋክቱራ እየተፈጠረ ነው…",
  noticeInvoiceCreated: "ፋክቱራ ተፈጥሮ ተልኳል።",
  customerInfoLoading: "የደንበኛ መረጃ በመፈተሽ ላይ…",
  customerInfoComplete: "የደንበኛ መረጃ ተሟልቷል።",
  customerInfoIncomplete: "የደንበኛ መረጃ አልተሟላም፦",
  customerIssueNotVatRegistered: "ደንበኛው በተ.እ.ታ ተመዝግቦ አልታየም።",
  customerIssueMissingVat: "የግብር ምዝገባ ቁጥር ጠፍቷል ወይም ልክ ያልሆነ ነው።",
  customerIssueMissingCrn: "CRN (የንግድ ምዝገባ ቁጥር) ጠፍቷል ወይም ልክ ያልሆነ ነው።",
  customerIssueMissingAddress: "ብሔራዊ አድራሻ ጠፍቷል ወይም አልተሟላም።",
  lineItemIssueMissingRate: "ዋጋ ጠፍቷል",
  lineItemIssueMissingNameEn: "የእንግሊዝኛ ስም ጠፍቷል",
  lineItemIssueMissingNameAr: "የዓረብኛ ስም ጠፍቷል",
  lineItemIssueMissingDescription: "መግለጫ ጠፍቷል",
  validationCustomerIncomplete: "የተመረጠው ደንበኛ መረጃ አልተሟላም። እስኪስተካከል ድረስ የB2B ፋክቱራ ሊፈጠር አይችልም።",
  validationLineItemsIncomplete: "አንድ ወይም ከዚያ በላይ ዕቃዎች ለተ.እ.ታ ፋክቱራ የሚያስፈልግ መረጃ ይጎድላቸዋል።",
  tabRecentInvoices: "የቅርብ ጊዜ ፋክቱራዎች",
  invoiceNumberCol: "ፋክቱራ #",
  dateCol: "ቀን",
  typeCol: "ዓይነት",
  customerCol: "ደንበኛ",
  statusCol: "ሁኔታ",
  typeWalkIn: "ቀጥታ ደንበኛ",
  typeB2B: "የንግድ ደንበኛ",
  statusPaid: "ተከፍሏል",
  statusPrinted: "ታትሟል",
  statusDraft: "ደረቅ",
  statusSent: "ተልኳል",
  todaysInvoicesCount: (count) => `${count} ፋክቱራዎች ዛሬ`,
  todaysInvoicesTotal: "ጠቅላላ (SAR)",
  loadingInvoices: "ፋክቱራዎች እየተጫኑ ነው…",
  invoicesLoadError: "ፋክቱራዎችን መጫን አልተሳካም።",
  noInvoicesToday: "እስካሁን ዛሬ ፋክቱራ የለም።",
  itemSearchPlaceholder: "ዕቃ በስም / SKU ይቃኙ ወይም ይፈልጉ...",
  customerSearchPlaceholder: "የንግድ ደንበኛ በስም ወይም በከተማ ይፈልጉ...",
  addCustomerBtn: "ደንበኛ ጨምር",
  emptyCartMessage: "እስካሁን ዕቃዎች አልተጨመሩም። ዕቃዎችን ለመጨመር ከላይ ይፈልጉ።",
  noticeSubmitted: "ፋክቱራው ገብቷል።",
  noticeSubmittedAndPrinted: "ፋክቱራው ገብቶ ለፕሪንተር ተልኳል።",
  noticeDraftCreated: "ደረቅ ፋክቱራ ተፈጥሯል።",
  noticeInvoiceSent: "ፋክቱራው ተልኳል።",
  unitCol: "ክፍል",
  priceCol: "ዋጋ (SAR)",
  lineTotalCol: "ድምር",
  createCustomerTitle: "ደንበኛ ፍጠር",
  primaryLangSection: "ዋና (ዓረብኛ)",
  secondaryLangSection: "ሁለተኛ (እንግሊዝኛ)",
  identificationSection: "መለያ መረጃ",
  addressSection: "አድራሻ",
  fieldNameAr: "ስም (ዓረብኛ)",
  fieldNameEn: "ስም (እንግሊዝኛ)",
  fieldPhone: "ስልክ ቁጥር",
  fieldVat: "የግብር ምዝገባ ቁጥር",
  fieldVatOptional: "የግብር ምዝገባ ቁጥር (አማራጭ)",
  fieldBuyerIdLabel: "የመታወቂያ ዓይነት",
  fieldBuyerIdValue: "CRN (የንግድ ምዝገባ ቁጥር)",
  fieldBuildingNumber: "የህንፃ ቁጥር",
  fieldStreet: "መንገድ",
  fieldAdditionalNumber: "ተጨማሪ ቁጥር",
  fieldDistrict: "ክልል/ሰፈር",
  fieldCity: "ከተማ",
  fieldState: "ግዛት",
  fieldPostalCode: "የፖስታ ኮድ",
  fieldCountry: "ሀገር",
  scanDocumentBtn: "ሰነድ ቃኝ (AI)",
  scanningDocument: "ሰነድ እየተቃኘ ነው…",
  scanDocumentError: "ሰነዱን ማንበብ አልተቻለም። እባክዎ ቅጹን በእጅ ይሙሉ።",
  scanDocumentSuccess: "መስኮች ከሰነዱ ተሞልተዋል — ከማስቀመጥዎ በፊት እባክዎ ይገምግሙ።",
  modalSave: "ደንበኛ አስቀምጥ",
  modalSaving: "እየተቀመጠ ነው…",
  modalCancel: "ተወው",
  buyerIdLabelNone: "የለም",
  requiredFieldsMissing: "እባክዎ ሁሉንም አስፈላጊ መስኮች ይሙሉ።",
  vatInvalid: "ልክ ያልሆነ የግብር ቁጥር — 15 አሃዞች ሊኖሩት እና በ 3 መጀመር እና ማለቅ አለበት።",
  crnInvalid: "ልክ ያልሆነ CRN — 10 አሃዞች ሊኖሩት እና በ 1 ወይም 7 መጀመር አለበት።",
};
export const translations: Record<Locale, Translations> = { en, ar, am };
import { createContext, useContext } from "react";
interface LocaleContextValue {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: Translations;
  dir: "ltr" | "rtl";
}
export const LocaleContext = createContext<LocaleContextValue>({
  locale: "en",
  setLocale: () => {},
  t: en,
  dir: "ltr",
});
export const useLocale = () => useContext(LocaleContext);