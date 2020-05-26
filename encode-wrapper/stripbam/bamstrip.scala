package BamUtils

import java.io._

// strip out cigar strings and sequences/qualities from bam piped into stdin
// keeping only the following fields: 
//  1,2,3,4,5,7,8,9 
// the output is written to stdout and can be converted back to bam

object BamSeqStrip {
  def handleHeader(buffered:BufferedReader, out:BufferedWriter):(Int, String) = {
     var n:Int = 0
     var line = buffered.readLine
     while(line != null){
       if(line.startsWith("@")){
         out.write(line)
         out.write("\n")
         n += 1
         line = buffered.readLine
       } else {
         return (n, line)
       }
     }
     (n, line)
  }

  def stripseq(fields:Array[String], out:BufferedWriter):Unit = {
    var i = 0
    while(i < 9){ 
      // suppress the cigar string
      out.write( if(i == 5){ "1M" } else { fields(i) } )
      out.write("\t")   
      i += 1
    }
    // strip away the sequence and qualities 
    out.write("N\t#\n")  
  }

  def main(args:Array[String]):Unit = {
     val reader = new BufferedReader(new InputStreamReader(System.in))
     val out = new BufferedWriter(new OutputStreamWriter(System.out))
     var (nHeader, line) = handleHeader(reader, out)
     var reads:Long = 0
     while(line != null){
       reads += 1
       stripseq(line.split("\t"), out)
       line = reader.readLine 
     }
     out.flush()
     System.err.println("%d:%d".format(reads, nHeader))
  }
}
