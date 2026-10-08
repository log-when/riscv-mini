package mini

import org.scalatest.flatspec._
import org.scalatest.matchers.should._
import chiseltest._
import chiseltest.formal._
import chiseltest.formal.chaAnno._
import chisel3._

import chisel3.stage._
import chisel3.util._
import chisel3.util.experimental.BoringUtils
import chisel3.experimental.IO

import chisel3.experimental.{ChiselAnnotation, annotate}
import firrtl.annotations.{Annotation, MemoryArrayInitAnnotation, MemoryScalarInitAnnotation, ReferenceTarget}
import firrtl.stage._
import chiseltest.formal.SignalNameAnnotation._

import firrtl.backends.experimental.smt._
import junctions._

// class CacheProp(p: CacheConfig, nasti: NastiBundleParameters, xlen: Int) 
//   extends Cache(p, nasti, xlen){

//   assume()
//   val nastiWriteReqReady = io.nasti.aw.ready
//   chaAssume(this, "F nastiWriteReqReady")
//   val nastiReadReqReady = io.nasti.ar.ready
//   chaAssume(this, "F nastiReadReqReady")

//   val nastiReadReqFire = io.nasti.ar.fire
//   val nastiReadRespValid = io.nasti.r.valid
//   // val nastiReadRespFinsh = io.nasti.r.bits.last
//   // A total outer-module
//   chaAssume(this, "nastiReadReqFire -> X F (nastiReadRespValid U read_wrap_out)" )
//   // chaAssume(this, "memReadFire -> X F (memRespVal U (memRespVal && memRespFin))")

//   val nastiWriteReqFire = io.nasti.aw.fire
//   val nastiWriteMemReady = io.nasti.w.ready
//   // val nastiReadRespFinsh = io.nasti.r.bits.last
//   // A total outer-module
//   chaAssume(this, "nastiWriteReqFire -> X F (nastiWriteMemReady U write_wrap_out)" )

//   val nastiWriteRespValid = io.nasti.b.valid 
//   val nastiWriteRespFire = io.nasti.b.fire
//   chaAssume(this, "nastiWriteReqFire -> X F (nastiWriteRespValid U nastiWriteRespFire)" )

//   // val nastiWriteRespFire = RegNext(io.nasti.b.fire)
//   // dontTouch(nastiWriteRespFire)
//   val require = io.cpu.req.valid
//   val response = io.cpu.resp.valid
  
//   chaAssert(this, "require -> F response") 
// }

class ICacheProp(p: CacheConfig, nasti: NastiBundleParameters, xlen: Int) 
  extends Cache(p, nasti, xlen){
  
  val disWrite = !io.cpu.req.bits.mask.orR
  // assume(disWrite)

  val require = io.cpu.req.valid
  val response = io.cpu.resp.valid

  val nastiWriteReqReady = io.nasti.aw.ready
  chaAssume(this, "F nastiWriteReqReady")
  val nastiReadReqReady = io.nasti.ar.ready
//  // chaAssume(this, "F nastiReadReqReady")

  // modified 1:
  chaAssume(this, "(G !response) -> FG nastiReadReqReady")


  val nastiReadReqFire = io.nasti.ar.fire
  val nastiReadRespValid = io.nasti.r.valid
  val nastiReadRespFinsh = io.nasti.r.bits.last
  // A total outer-module
//  // chaAssume(this, "nastiReadReqFire -> X F (nastiReadRespValid U read_wrap_out)" )
//  // chaAssume(this, "nastiReadReqFire -> X F (nastiReadRespValid U (nastiReadRespValid && nastiReadRespFinsh))")
//  // chaAssume(this, "nastiReadReqFire -> X (!nastiReadRespValid U (nastiReadRespValid & !nastiReadRespFinsh) ##1 (nastiReadRespValid & nastiReadRespFinsh))")
  chaAssume(this, "nastiReadReqFire -> X F nastiReadRespValid")
  chaAssume(this, "nastiReadRespValid -> X (nastiReadRespValid U (nastiReadRespValid & nastiReadRespFinsh))")

  val nastiWriteReqFire = io.nasti.aw.fire
  val nastiWriteMemReady = io.nasti.w.ready
  val nastiWriteRespFinsh = io.nasti.w.bits.last
  // A total outer-module
  chaAssume(this, "nastiWriteReqFire -> X F (nastiWriteMemReady U (nastiWriteMemReady && nastiWriteRespFinsh))" )
//  // chaAssume(this, "nastiWriteReqFire -> X F (nastiWriteMemReady U nastiReadRespFinsh)" )

  val nastiWriteRespValid = io.nasti.b.valid 
  val nastiWriteRespFire = io.nasti.b.fire
  chaAssume(this, "nastiWriteReqFire -> X F (nastiWriteRespValid U nastiWriteRespFire)" )

  // val nastiWriteRespFire = RegNext(io.nasti.b.fire)
  // dontTouch(nastiWriteRespFire)

  
  // chaAssert(this, "FG !require -> FG response") 
  chaAssert(this, "F response") 
}

class DCacheProp(p: CacheConfig, nasti: NastiBundleParameters, xlen: Int) 
  extends Cache(p, nasti, xlen){
  
  // val disWrite = !io.cpu.req.bits.mask.orR
  // assume(disWrite)

//   assume()
  val nastiWriteReqReady = io.nasti.aw.ready
  chaAssume(this, "F nastiWriteReqReady")
  val nastiReadReqReady = io.nasti.ar.ready
  chaAssume(this, "F nastiReadReqReady")

  val nastiReadReqFire = io.nasti.ar.fire
  val nastiReadRespValid = io.nasti.r.valid
  val nastiReadRespFinsh = io.nasti.r.bits.last
  // A total outer-module
//  // chaAssume(this, "nastiReadReqFire -> X F (nastiReadRespValid U read_wrap_out)" )
//  // chaAssume(this, "nastiReadReqFire -> X F (nastiReadRespValid U (nastiReadRespValid && nastiReadRespFinsh))")
//  // chaAssume(this, "nastiReadReqFire -> X (!nastiReadRespValid U (nastiReadRespValid & !nastiReadRespFinsh) ##1 (nastiReadRespValid & nastiReadRespFinsh))")
  chaAssume(this, "nastiReadReqFire -> X F nastiReadRespValid")
  chaAssume(this, "nastiReadRespValid -> X (nastiReadRespValid U (nastiReadRespValid & nastiReadRespFinsh))")

  val nastiWriteReqFire = io.nasti.aw.fire
  val nastiWriteMemReady = io.nasti.w.ready
  val nastiWriteRespFinsh = io.nasti.w.bits.last
  // A total outer-module
  chaAssume(this, "nastiWriteReqFire -> X F (nastiWriteMemReady U (nastiWriteMemReady && nastiWriteRespFinsh))" )
//  // chaAssume(this, "nastiWriteReqFire -> X F (nastiWriteMemReady U nastiReadRespFinsh)" )

  val nastiWriteRespValid = io.nasti.b.valid 
  val nastiWriteRespFire = io.nasti.b.fire
  chaAssume(this, "nastiWriteReqFire -> X F (nastiWriteRespValid U nastiWriteRespFire)" )

  // val nastiWriteRespFire = RegNext(io.nasti.b.fire)
  // dontTouch(nastiWriteRespFire)
  val require = io.cpu.req.valid
  val response = io.cpu.resp.valid
  
  // chaAssert(this, "FG !require -> FG response") 
  // chaAssert(this, "F response") 

  // th 1.1 (fake)
  // chaAssert(this, "G !response -> FG !require") 

  // th 1.2
  val nastiWriteReqValid = io.nasti.aw.valid
  // chaAssert(this, "(G !require) -> FG !nastiWriteReqValid") 

  // th 1.3
  val nastiReadReqValid = io.nasti.ar.valid
  // chaAssert(this, "(G !require) -> FG !nastiWriteReqValid") 
  
  // th 1.4
  // chaAssert(this, "(G !require) -> FG is_idle") 

  // is_idle
  // val nastiWriteReqValid = io.nasti.aw.valid

}

class CachePropSpec extends AnyFlatSpec with ChiselScalatestTester with Formal {

  val config = MiniConfig()

  // testcase 31
  behavior of "ICacheProp"
  it should "pass" in {
    verify(new ICacheProp(config.cache, config.nasti, config.core.xlen), Seq(BoundedCheck(20), PonoEngineAnnotation))
    // verify(new ICacheProp(config.cache, config.nasti, config.core.xlen), Seq(Ic3Check(20), RIC3EngineAnnotation))
  }

  // behavior of "DCacheProp"
  // it should "pass" in {
  //   // verify(new CacheProp(config.cache, config.nasti, config.core.xlen), Seq(BoundedCheck(20), PonoEngineAnnotation))
  //   verify(new DCacheProp(config.cache, config.nasti, config.core.xlen), Seq(Ic3Check(20), RIC3EngineAnnotation))
  // }
  // AVR (AVREngineAnnotation) is not stable
  // testcase 30
  // behavior of "CacheStage2"
  // it should "pass" in {
  //   verify(new CacheStage2Prop()(new CacheConfig()), Seq(BoundedCheck(20), PonoEngineAnnotation))
  // }


  // testcase 32
  // behavior of "CacheStage3"
  // it should "pass" in {
  //   verify(new CacheStage3Prop()(new CacheConfig()), Seq(BoundedCheck(20), PonoEngineAnnotation))
  // }

  // testcase 32
  // behavior of "CacheArray"
  // it should "pass" in {
  //   verify(new CacheArrayProp()(new CacheConfig()), Seq(BoundedCheck(20), PonoEngineAnnotation))
  // }
  
}