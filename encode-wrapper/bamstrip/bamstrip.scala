package BamUtils

import java.io._

// strip out cigar strings and sequences/qualities from bam piped into stdin
// keeping only the following fields: 
//  1,2,3,4,5,7,8,9
// cigar string is replaced by 1M, sequence by N, qualities by #
// the output is written to stdout and can be converted back to bam

/*
SAM format specification: https://samtools.github.io/hts-specs/SAMv1.pdf

Col Field Type Regexp/Range Brief description
1 QNAME String [!-?A-~]{1,254} Query template NAME
2 FLAG Int [0, 216 −1] bitwise FLAG
3 RNAME String \*|[:rname:∧*=][:rname:]* Reference sequence NAME^11
4 POS Int [0, 231 −1] 1-based leftmost mapping POSition
5 MAPQ Int [0, 28 −1] MAPping Quality
6 CIGAR String \*|([0-9]+[MIDNSHPX=])+ CIGAR string
7 RNEXT String \*|=|[:rname:∧*=][:rname:]* Reference name of the mate/next read
8 PNEXT Int [0, 231 −1] Position of the mate/next read
9 TLEN Int [− 231 + 1, 231 −1] observed Template LENgth
10 SEQ String \*|[A-Za-z=.]+ segment SEQuence
11 QUAL String [!-~]+ ASCII of Phred-scaled base QUALity+
*/

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
     System.err.println("#__bamstrip__ summary %d:%d".format(reads, nHeader))
  }
}
