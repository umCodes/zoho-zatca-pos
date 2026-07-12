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
}
const en: Translations = {
  appTitle: "Simple Zoho POS",
  searchItem: "Search Item",
  orderSummary: "Order Summary",
  itemName: "Item Name",
  quantity: "Quantity",
  price: "Price",
  total: "Total",
  subtotal: "Subtotal",
  vat: "VAT",
  vatPercent: "VAT (15%)",
  grandTotal: "Total",
  submitOrder: "Submit",
  submitNPrintOrder: "Submit & Print",
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
};
const ar: Translations = {
  appTitle: "نقطة بيع زوهو البسيطة",
  searchItem: "ابحث عن صنف",
  orderSummary: "ملخص الطلب",
  itemName: "اسم الصنف",
  quantity: "الكمية",
  price: "السعر",
  total: "الإجمالي",
  subtotal: "المجموع الفرعي",
  vat: "ضريبة القيمة المضافة",
  vatPercent: "ضريبة القيمة المضافة (١٥٪)",
  grandTotal: "الإجمالي الكلي",
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
};
const am: Translations = {
  appTitle: "Simple Zoho POS",
  searchItem: "ዕቃ ፈልግ",
  orderSummary: "የትዕዛዝ ማጠቃለያ",
  itemName: "የዕቃ ስም",
  quantity: "ብዛት",
  price: "ዋጋ",
  total: "ድምር",
  subtotal: "ንዑስ ድምር",
  vat: "VAT",
  vatPercent: "ተ.እ.ታ (15%)",
  grandTotal: "ጠቅላላ ድምር",
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