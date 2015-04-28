import android.util.Log;

public class Injector {
  private static String log_tag = "Trevillie";
  private static String log_content = "This is for the test of log cleaning functionality.";
  private static String start_tag = "apeDroid";
  private static String start_content = "This is for the test of app startup timing.";

  public static void main(String[] args){
    test_logging();
  }

  public static void test_logging(){
    Log.v(log_tag, log_content);
    Log.d(log_tag, log_content);
    Log.i(log_tag, log_content);
    Log.w(log_tag, log_content);
    Log.e(log_tag, log_content);
  }

  public static void test_startup_time(){
    Log.e(start_tag, start_content);
  }
}
