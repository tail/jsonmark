package im.tail.jsonmark.deserializer;

import java.io.IOException;
import java.util.Date;

import com.google.common.io.LineProcessor;

import io.vertx.core.Vertx;
import io.vertx.core.file.AsyncFile;
import io.vertx.core.file.FileSystem;
import io.vertx.core.file.OpenOptions;
import io.vertx.core.parsetools.RecordParser;

public class App {
    private static Vertx vertx;
    private static boolean done;

    public static class MyLineProcessor implements LineProcessor<Void> {
        public boolean processLine(String line) throws IOException {
            return true;
        }

        public Void getResult() {
            return null;
        }

    }

    public static void main(String[] args) {
        done = false;
        if (args.length != 2) {
            System.out.println("requires two args: <benchmark> <filename>");
            System.exit(1);
        }

        // Files.readLines using LineProcessor
        //
        // var file = new File(args[1]);
        // try {
        //     // Files.readLines(file, Charsets.UTF_8, new MyLineProcessor());
        //     var charSource = Files.asCharSource(file, Charsets.UTF_8);
        //     charSource.readLines(new MyLineProcessor());
        // } catch (IOException ex) {
        //     System.out.println("Got exception: " + ex.toString());
        //     System.exit(1);
        // }

        // Using BufferedReader
        //
        // var file = new File(args[1]);
        // String line;
        // try {
        //     var fr = new FileReader(file);
        //     var br = new BufferedReader(fr);
        //     int i = 0;
        //     while ((line = br.readLine()) != null) {
        //         i += 1;
        //         if (i % 100000 == 0) {
        //             // System.gc();
        //         }
        //     }
        //     br.close();
        // } catch (FileNotFoundException ex) {
        //     System.out.println("Got exception: " + ex.toString());
        //     System.exit(1);
        // } catch(IOException ex) {
        //     System.out.println("Got exception: " + ex.toString());
        //     System.exit(1);
        // }

        System.out.println(new Date() + " Starting");
        vertx = Vertx.vertx();
        FileSystem fs = vertx.fileSystem();
        RecordParser recordParser = RecordParser.newDelimited("\n", bufferedLine -> {
            // System.out.println("line = " + bufferedLine);
        });
        AsyncFile asyncFile = fs.openBlocking(args[1], new OpenOptions().setRead(true));
        asyncFile.handler(recordParser)
            .endHandler(v -> {
                asyncFile.close();
                vertx.close();
                System.out.println(new Date() + " Done!");
            });

        System.out.println("Waiting to finish...");

        

        // Using Files.lines
        //
        // var path = Paths.get(args[1]);
        // try {
        //     var lines = Files.lines(path);
        //     lines.forEach(s -> {
        //         // var obj = JSONObject.parse(s);
        //         // System.out.println(JSONObject.class.cast(obj).getInteger("integer_1"));
        //     });
        //     lines.close();
        // } catch(IOException ex) {
        //     System.out.println("IOException: " + ex.toString());
        //     System.exit(1);
        // }
    }
}
