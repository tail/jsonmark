package im.tail.jsonmark.deserializer;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

import com.alibaba.fastjson.JSONObject;

public class App {
    public static void main(String[] args) {
        if (args.length != 2) {
            System.out.println("requires two args: <benchmark> <filename>");
            System.exit(1);
        }

        var path = Paths.get(args[1]);
        try {
            var lines = Files.lines(path);
            lines.forEach(s -> {
                var obj = JSONObject.parse(s);
                System.out.println(JSONObject.class.cast(obj).getInteger("integer_1"));
            });
            lines.close();
        } catch(IOException ex) {
            System.out.println("IOException: " + ex.toString());
            System.exit(1);
        }
    }
}
