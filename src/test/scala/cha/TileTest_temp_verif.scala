// package mini

// import org.scalatest.flatspec._
// import org.scalatest.matchers.should._
// import chiseltest._
// import chiseltest.formal._
// import chiseltest.formal.chaAnno._
// import chisel3._

// import chisel3.stage._
// import chisel3.util._
// import chisel3.util.experimental.BoringUtils
// import chisel3.experimental.IO

// import chisel3.experimental.{ChiselAnnotation, annotate}
// import firrtl.annotations.{Annotation, MemoryArrayInitAnnotation, MemoryScalarInitAnnotation, ReferenceTarget}
// import firrtl.stage._
// import chiseltest.formal.SignalNameAnnotation._

// import firrtl.backends.experimental.smt._
// import junctions._

// class DatapathProp(coreParams: CoreConfig) extends Datapath(coreParams){
  

  // val s1_gen_by10_in_DatapathProp = io.icache.req.valid
  // SignalName(s1_gen_by10_in_DatapathProp,9)
  // val s9_gen_by8_in_DatapathProp = io.dcache.resp.valid
  // SignalName(s9_gen_by8_in_DatapathProp,10)
  // val s8_gen_by10_in_ICacheProp_0_der_in_DatapathProp_0_from_and_0 = io.icache.resp.valid
  // SignalName(s8_gen_by10_in_ICacheProp_0_der_in_DatapathProp_0_from_and_0,11)
  // val s4_gen_by4_in_ICacheProp_0_der_in_DatapathProp_0_from_and_0 = io.icache.abort
  // SignalName(s4_gen_by4_in_ICacheProp_0_der_in_DatapathProp_0_from_and_0,12)
  // val s4_gen_by10_in_ICacheProp_0_der_in_DatapathProp_0_from_and_0 = io.icache.req.bits.mask.orR
  // SignalName(s4_gen_by10_in_ICacheProp_0_der_in_DatapathProp_0_from_and_0,13)
  // val s9_gen_by5_in_ControlProp_0_der_in_DatapathProp_0_from_and_0 = io.ctrl.inst_kill
  // SignalName(s9_gen_by5_in_ControlProp_0_der_in_DatapathProp_0_from_and_0,14)
// }

// class ControlProp() extends Control(){


  // val s9_gen_by5_in_ControlProp = io.inst_kill
  // SignalName(s9_gen_by5_in_ControlProp,18)
// } 

// class DCacheProp(p: CacheConfig, nasti: NastiBundleParameters, xlen: Int) 
  // extends Cache(p, nasti, xlen){


  // val s2_gen_by10_in_DCacheProp = io.cpu.resp.valid
  // SignalName(s2_gen_by10_in_DCacheProp,15)
  // val s7_gen_by10_in_MemArbiterProp_0_der_in_DCacheProp_0_from_and_0 = io.nasti.ar.valid
  // SignalName(s7_gen_by10_in_MemArbiterProp_0_der_in_DCacheProp_0_from_and_0,16)
  // val s9_gen_by10_in_MemArbiterProp_0_der_in_DCacheProp_0_from_and_0 = io.nasti.aw.valid
  // SignalName(s9_gen_by10_in_MemArbiterProp_0_der_in_DCacheProp_0_from_and_0,17)
// }

// class ICacheProp(p: CacheConfig, nasti: NastiBundleParameters, xlen: Int) 
  // extends Cache(p, nasti, xlen){


  // val s8_gen_by10_in_ICacheProp = io.cpu.resp.valid
  // SignalName(s8_gen_by10_in_ICacheProp,19)
  // val s0_gen_by10_in_ICacheProp = io.cpu.req.valid
  // SignalName(s0_gen_by10_in_ICacheProp,20)
  // val s0_gen_by2_in_ICacheProp = io.nasti.r.fire
  // SignalName(s0_gen_by2_in_ICacheProp,21)
  // val s4_gen_by7_in_ICacheProp = io.nasti.ar.fire
  // SignalName(s4_gen_by7_in_ICacheProp,22)
  // val s2_gen_by5_in_ICacheProp = io.nasti.r.bits.last
  // SignalName(s2_gen_by5_in_ICacheProp,23)
  // val s9_gen_by2_in_ICacheProp = !io.cpu.req.bits.mask.orR
  // SignalName(s9_gen_by2_in_ICacheProp,24)
  // val s4_gen_by4_in_ICacheProp = io.cpu.abort
  // SignalName(s4_gen_by4_in_ICacheProp,25)
  // val s8_gen_by5_in_ICacheProp = io.nasti.r.valid
  // SignalName(s8_gen_by5_in_ICacheProp,26)
  // val s4_gen_by10_in_ICacheProp = io.cpu.req.bits.mask.orR
  // SignalName(s4_gen_by10_in_ICacheProp,27)
  // val s1_gen_by7_in_ICacheProp = (io.nasti.r.valid && io.nasti.r.bits.last)
  // SignalName(s1_gen_by7_in_ICacheProp,28)
  // val s5_gen_by9_in_MemArbiterProp_0_der_in_ICacheProp_0_from_and_0 = io.nasti.ar.ready
  // SignalName(s5_gen_by9_in_MemArbiterProp_0_der_in_ICacheProp_0_from_and_0,29)
  // val s6_gen_by10_in_MemArbiterProp_0_der_in_ICacheProp_0_from_and_0 = io.nasti.ar.valid
  // SignalName(s6_gen_by10_in_MemArbiterProp_0_der_in_ICacheProp_0_from_and_0,30)

// chaAssert(this, "(G ((!s6_gen_by10_in_MemArbiterProp_0_der_in_ICacheProp_0_from_and_0))) -> F G ((!s0_gen_by2_in_ICacheProp))") 
// }

// class MemArbiterProp(params: NastiBundleParameters) extends MemArbiter(params){

  // val nastiWriteReqReady = io.nasti.aw.ready
  // chaAssume(this, "F nastiWriteReqReady")
  // val nastiReadReqReady = io.nasti.ar.ready
  // chaAssume(this, "F nastiReadReqReady")

  // val nastiReadReqFire = io.nasti.ar.fire
  // val nastiReadRespValid = io.nasti.r.valid
  // val nastiReadRespFinsh = io.nasti.r.bits.last
  // chaAssume(this, "nastiReadReqFire -> X (!nastiReadRespValid U (nastiReadRespValid & !nastiReadRespFinsh) ##1 (nastiReadRespValid & nastiReadRespFinsh))")

  // val nastiWriteReqFire = io.nasti.aw.fire
  // val nastiWriteMemReady = io.nasti.w.ready
  // val nastiWriteRespFinsh = io.nasti.w.bits.last
  // // A total outer-module
  // // used to constrain ready
  // chaAssume(this, "nastiWriteReqFire -> X F (nastiWriteMemReady U (nastiWriteMemReady && nastiWriteRespFinsh))" )
  // // chaAssume(this, "nastiWriteReqFire -> X F (nastiReadRespValid U (nastiReadRespValid && nastiReadRespFinsh))")

  // val nastiWriteRespValid = io.nasti.b.valid 
  // val nastiWriteRespFire = io.nasti.b.fire
  // chaAssume(this, "nastiWriteReqFire -> X F (nastiWriteRespValid U nastiWriteRespFire)" )


  // val s3_gen_by5_in_MemArbiterProp = io.icache.r.bits.last
  // SignalName(s3_gen_by5_in_MemArbiterProp,1)
  // val s10_gen_by10_in_MemArbiterProp = io.icache.ar.fire
  // SignalName(s10_gen_by10_in_MemArbiterProp,2)
  // val s5_gen_by5_in_MemArbiterProp = io.icache.r.valid
  // SignalName(s5_gen_by5_in_MemArbiterProp,3)
  // val s5_gen_by9_in_MemArbiterProp = io.icache.ar.ready
  // SignalName(s5_gen_by9_in_MemArbiterProp,4)
  // val s6_gen_by10_in_MemArbiterProp = io.icache.ar.valid
  // SignalName(s6_gen_by10_in_MemArbiterProp,5)
  // val s7_gen_by10_in_MemArbiterProp = io.dcache.ar.valid
  // SignalName(s7_gen_by10_in_MemArbiterProp,6)
  // val s9_gen_by10_in_MemArbiterProp = io.dcache.aw.valid
  // SignalName(s9_gen_by10_in_MemArbiterProp,7)
  // val s0_gen_by2_in_ICacheProp_0_der_in_MemArbiterProp_0_from_and_0 = io.icache.r.fire
  // SignalName(s0_gen_by2_in_ICacheProp_0_der_in_MemArbiterProp_0_from_and_0,8)
// }

// class TileProp(val coreParams: CoreConfig, val nastiParams: NastiBundleParameters, val cacheParams: CacheConfig) extends Module{

  // val dpath = Module(new DatapathProp(coreParams))
  // val ctrl = Module(new ControlProp)

  // val icache = Module(new ICacheProp(cacheParams, nastiParams, coreParams.xlen))
  // val dcache = Module(new DCacheProp(cacheParams, nastiParams, coreParams.xlen))
  // val arb = Module(new MemArbiterProp(nastiParams))

  // dpath.io.host := DontCare
  // dpath.io.icache <> icache.io.cpu
  // dpath.io.dcache <> dcache.io.cpu
  // arb.io.icache <> icache.io.nasti
  // arb.io.dcache <> dcache.io.nasti
  // arb.io.nasti := DontCare

  // dpath.io.ctrl <> ctrl.io
// }

// class TileSignal extends AnyFlatSpec with ChiselScalatestTester with Formal {

  // val config = MiniConfig()

  // (new ChiselStage).execute(
      // Array(),
      // Seq(
          // ChiselGeneratorAnnotation(() => new DatapathProp(config.core)),
          // RunFirrtlTransformAnnotation(PrintSignalNames)
      // )
  // )

  // (new ChiselStage).execute(
      // Array(),
      // Seq(
          // ChiselGeneratorAnnotation(() => new ControlProp()),
          // RunFirrtlTransformAnnotation(PrintSignalNames)
      // )
  // )

  // (new ChiselStage).execute(
      // Array(),
      // Seq(
          // ChiselGeneratorAnnotation(() => new ICacheProp(config.cache, config.nasti, config.core.xlen)),
          // RunFirrtlTransformAnnotation(PrintSignalNames)
      // )
  // )

  // (new ChiselStage).execute(
      // Array(),
      // Seq(
          // ChiselGeneratorAnnotation(() => new DCacheProp(config.cache, config.nasti, config.core.xlen)),
          // RunFirrtlTransformAnnotation(PrintSignalNames)
      // )
  // )

  // (new ChiselStage).execute(
      // Array(),
      // Seq(
          // ChiselGeneratorAnnotation(() => new MemArbiterProp(config.nasti)),
          // RunFirrtlTransformAnnotation(PrintSignalNames)
      // )
  // )

  // // (new ChiselStage).execute(
  // //     Array(),
  // //     Seq(
  // //         ChiselGeneratorAnnotation(() => new TileProp(config.core, config.nasti, config.cache)),
  // //         RunFirrtlTransformAnnotation(PrintSignalNames)
  // //     )
  // // )
// }
// // class TileFlatProp(val coreParams: CoreConfig, val nastiParams: NastiBundleParameters, val cacheParams: CacheConfig)
// //   extends Module{
// //   val io = IO(new TileIO(coreParams.xlen, nastiParams))

// //   val dpath = Module(new Datapath(coreParams))
// //   val ctrl = Module(new Control)

// //   val icache = Module(new Cache(cacheParams, nastiParams, coreParams.xlen))
// //   val dcache = Module(new Cache(cacheParams, nastiParams, coreParams.xlen))
// //   val arb = Module(new MemArbiter(nastiParams))

// //   dpath.io.host <> io.host
// //   dpath.io.icache <> icache.io.cpu
// //   dpath.io.dcache <> dcache.io.cpu
// //   arb.io.icache <> icache.io.nasti
// //   arb.io.dcache <> dcache.io.nasti
// //   io.nasti <> arb.io.nasti

// //   dpath.io.ctrl <> ctrl.io
  
// //   val en_fetch = icache.io.cpu.resp.valid
// //   val en_wb = ctrl.io.wb_en && (icache.io.cpu.resp.valid && icache.io.cpu.resp.valid) && dcache.io.cpu.abort


// //   val nastiWriteReqReady = io.nasti.aw.ready
// //   chaAssume(this, "F nastiWriteReqReady")
// //   val nastiReadReqReady = io.nasti.ar.ready
// //   chaAssume(this, "F nastiReadReqReady")

// //   val nastiReadReqFire = io.nasti.ar.fire
// //   val nastiReadRespValid = io.nasti.r.valid
// //   val nastiReadRespFinsh = io.nasti.r.bits.last
// //   // A total outer-module
// //   // chaAssume(this, "nastiReadReqFire -> X F (nastiReadRespValid U read_wrap_out)" )
// //   // chaAssume(this, "nastiReadReqFire -> X F ((nastiReadRespValid & !nastiReadRespFinsh) ##1 (nastiReadRespValid & nastiReadRespFinsh))")
// //   // chaAssume(this, "nastiReadReqFire -> X (!nastiReadRespValid U (nastiReadRespValid & !nastiReadRespFinsh) ##1 (nastiReadRespValid & nastiReadRespFinsh))")
// //   chaAssume(this, "nastiReadReqFire -> X (!nastiReadRespValid U (nastiReadRespValid & !nastiReadRespFinsh) ##1 (nastiReadRespValid & nastiReadRespFinsh))")

// //   val nastiWriteReqFire = io.nasti.aw.fire
// //   val nastiWriteMemReady = io.nasti.w.ready
// //   val nastiWriteRespFinsh = io.nasti.w.bits.last
// //   // A total outer-module
// //   // used to constrain ready
// //   chaAssume(this, "nastiWriteReqFire -> X F (nastiWriteMemReady U (nastiWriteMemReady && nastiWriteRespFinsh))" )
// //   // chaAssume(this, "nastiWriteReqFire -> X F (nastiReadRespValid U (nastiReadRespValid && nastiReadRespFinsh))")

// //   val nastiWriteRespValid = io.nasti.b.valid 
// //   val nastiWriteRespFire = io.nasti.b.fire
// //   chaAssume(this, "nastiWriteReqFire -> X F (nastiWriteRespValid U nastiWriteRespFire)" )

// //   // io.icache.req.valid
// //   // regFile.io.wen := wb_en && !stall && !csr.io.expt
// //   chaAssert(this, "F en_fetch") 

// //   // chaAssert(this, "F en_wb") 
// // }


// class TileFlatPropSpec extends AnyFlatSpec with ChiselScalatestTester with Formal {

  // val config = MiniConfig()

  // // behavior of "Datapath"
  // // it should "pass" in {
  // //   verify(new DatapathProp(config.core), Seq(Ic3Check(20), RIC3EngineAnnotation))
  // // }

  // // behavior of "Control"
  // // it should "pass" in {
  // //   verify(new ControlProp(), Seq(Ic3Check(20), RIC3EngineAnnotation))
  // // }

  // behavior of "ICache"
  // it should "pass" in {
    // verify(new ICacheProp(config.cache, config.nasti, config.core.xlen), Seq(Ic3Check(20), RIC3EngineAnnotation))
  // }

  // // behavior of "DCache"
  // // it should "pass" in {
  // //   verify(new DCacheProp(config.cache, config.nasti, config.core.xlen), Seq(Ic3Check(20), RIC3EngineAnnotation))
  // // }

  // // behavior of "MemArbiter"
  // // it should "pass" in {
  // //   verify(new MemArbiterProp(config.nasti), Seq(Ic3Check(20), RIC3EngineAnnotation))
  // // }

// }