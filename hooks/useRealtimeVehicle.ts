import { useState, useEffect } from "react";
import type { Vehicle } from "@/lib/types";

// هر زمان سوپابیس رو به پروژه اضافه کردی (npm install @supabase/supabase-js)
// و کلاینتش رو ساختی، این خط رو از کامنت در بیار:
// import { supabase } from "@/lib/supabaseClient"; 

export function useRealtimeVehicle(initialVehicle: Vehicle | null) {
  const [liveVehicle, setLiveVehicle] = useState<Vehicle | null>(initialVehicle);

  useEffect(() => {
    // هربار که کاربر روی یک وسیله جدید کلیک کرد، دیتای اولیه رو ست کن
    setLiveVehicle(initialVehicle);
    
    if (!initialVehicle) return;

    // --- کدهای اتصال زنده به سوپابیس ---
    // وقتی دیتابیس آماده شد، این بخش رو از کامنت در بیار تا سایتت واقعاً زنده بشه!
    
    /*
    const channel = supabase
      .channel(`live-vehicle-${initialVehicle.id}`)
      .on(
        "postgres_changes",
        {
          event: "UPDATE",
          schema: "public",
          table: "vehicles", // اسم تیبل دیتابیست
          filter: `id=eq.${initialVehicle.id}`, // فقط تغییرات همین وسیله رو گوش بده
        },
        (payload) => {
          console.log("🔥 Live update received from bot!", payload.new);
          // آپدیت کردن استیت با دیتای جدید ربات
          setLiveVehicle(payload.new as Vehicle);
        }
      )
      .subscribe();

    return () => {
      // وقتی کاربر مدال رو بست، اتصال رو قطع کن تا رم سیستم پر نشه
      supabase.removeChannel(channel);
    };
    */

  }, [initialVehicle]);

  return liveVehicle;
}
