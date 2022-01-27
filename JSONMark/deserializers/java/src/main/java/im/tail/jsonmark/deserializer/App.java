package im.tail.jsonmark.deserializer;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;

import com.alibaba.fastjson.JSONObject;

public class App {
    public static int checksum = 0;

    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("requires one arg: <filename>");
            System.exit(1);
        }

        // NOTE: BufferedReader and Files.lines perform similar (~0.6s for 1M
        // record 333MiB file).  com.google.common.io.LineProcessor and vertx
        // were both even slower.

        // Using BufferedReader
        //
        var file = new File(args[0]);
        String line;
        try {
            var fr = new FileReader(file);
            var br = new BufferedReader(fr);
            while ((line = br.readLine()) != null) {
                var obj = JSONObject.parse(line);
                checksum += JSONObject.class.cast(obj).getInteger("integer_1") + JSONObject.class.cast(obj).getInteger("integer_2");
            }
            br.close();
        } catch (IOException ex) {
            System.out.println("Got exception: " + ex.toString());
            System.exit(1);
        }

        // Using Files.lines
        //
        // var path = Paths.get(args[0]);
        // try {
        //     var lines = Files.lines(path);
        //     lines.forEach(s -> {
        //         var obj = JSONObject.parse(s);
        //         checksum += JSONObject.class.cast(obj).getInteger("integer_1") + JSONObject.class.cast(obj).getInteger("integer_2");
        //     });
        //     lines.close();
        // } catch(IOException ex) {
        //     System.out.println("IOException: " + ex.toString());
        //     System.exit(1);
        // }

        System.out.println(checksum);
    }
}
