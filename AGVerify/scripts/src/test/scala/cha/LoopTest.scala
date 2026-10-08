package mini
import org.scalatest.flatspec._
import chiseltest._
import chiseltest.formal._
import chisel3.stage._
import chiseltest.formal.chaAnno._
class LoopTest extends AnyFlatSpec with ChiselScalatestTester {
  it should "elaborate" in {
    (new ChiselStage).execute(Array(), Seq(
      ChiselGeneratorAnnotation(() => new mini.AGDCacheProp(
        (new MiniConfig).cache, (new MiniConfig).nasti, 32))))
  }
}
