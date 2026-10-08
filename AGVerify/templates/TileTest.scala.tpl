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

// ======================================================================
// 本文件由 AGVerify cha_verify.py 生成, 勿手工编辑
// ======================================================================

class AGDatapathProp(coreParams: CoreConfig) extends Datapath(coreParams){
@DATAPATH_BODY@
}

class AGControlProp() extends Control(){
@CONTROL_BODY@
}

class AGDCacheProp(p: CacheConfig, nasti: NastiBundleParameters, xlen: Int)
  extends Cache(p, nasti, xlen){
@DCACHE_BODY@
}

class AGICacheProp(p: CacheConfig, nasti: NastiBundleParameters, xlen: Int)
  extends Cache(p, nasti, xlen){
@ICACHE_BODY@
}

class AGMemArbiterProp(params: NastiBundleParameters) extends MemArbiter(params){
@MEMARBITER_BODY@
}

// 编译检查入口: 生成 anno.json (信号编号 <-> FIRRTL 信号名映射),
// 不运行求解器
class AGTileSignal extends AnyFlatSpec with ChiselScalatestTester with Formal {

  val config = MiniConfig()

  (new ChiselStage).execute(
      Array(),
      Seq(
          ChiselGeneratorAnnotation(() => new AGDatapathProp(config.core)),
          RunFirrtlTransformAnnotation(PrintSignalNames)
      )
  )

  (new ChiselStage).execute(
      Array(),
      Seq(
          ChiselGeneratorAnnotation(() => new AGControlProp()),
          RunFirrtlTransformAnnotation(PrintSignalNames)
      )
  )

  (new ChiselStage).execute(
      Array(),
      Seq(
          ChiselGeneratorAnnotation(() => new AGICacheProp(config.cache, config.nasti, config.core.xlen)),
          RunFirrtlTransformAnnotation(PrintSignalNames)
      )
  )

  (new ChiselStage).execute(
      Array(),
      Seq(
          ChiselGeneratorAnnotation(() => new AGDCacheProp(config.cache, config.nasti, config.core.xlen)),
          RunFirrtlTransformAnnotation(PrintSignalNames)
      )
  )

  (new ChiselStage).execute(
      Array(),
      Seq(
          ChiselGeneratorAnnotation(() => new AGMemArbiterProp(config.nasti)),
          RunFirrtlTransformAnnotation(PrintSignalNames)
      )
  )
}

class AGTileFlatProp(val coreParams: CoreConfig, val nastiParams: NastiBundleParameters, val cacheParams: CacheConfig)
  extends Module{

  val io = IO(new TileIO(coreParams.xlen, nastiParams))

  // 实例化 *Prop 子类: 各模块的先验假设(chaAssume)在全局验证中常驻
  val dpath = Module(new AGDatapathProp(coreParams))
  val ctrl = Module(new AGControlProp())

  val icache = Module(new AGICacheProp(cacheParams, nastiParams, coreParams.xlen))
  val dcache = Module(new AGDCacheProp(cacheParams, nastiParams, coreParams.xlen))
  val arb = Module(new AGMemArbiterProp(nastiParams))

  dpath.io.host <> io.host
  dpath.io.icache <> icache.io.cpu
  dpath.io.dcache <> dcache.io.cpu
  arb.io.icache <> icache.io.nasti
  arb.io.dcache <> dcache.io.nasti
  io.nasti <> arb.io.nasti

  dpath.io.ctrl <> ctrl.io
@TILE_BODY@
}

// 空设计蕴含检查: 全部信号为自由 Bool 输入（同一物理信号的多个别名
// 绑定同一输入）, 子性质作 assume, 目标性质作 assert, IC3 纯逻辑验证
class AGImplicationProp extends Module {
  val io = IO(new Bundle {
@IMPL_IO@
  })
@IMPL_BODY@
}

class AGTileFlatPropSpec extends AnyFlatSpec with ChiselScalatestTester with Formal {

  val config = MiniConfig()
@VERIFY_LINES@
}
