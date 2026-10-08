// // See LICENSE for license details.

// package mini

// import chisel3._
// import chisel3.util._
// import junctions._
// import chisel3.util.BitPat
// import chisel3.experimental.BundleLiterals._

// object Main extends App {
//   val config = MiniConfig()
//   ChiselStage.emitSystemVerilogFile(
//     new Tile(
//       coreParams = config.core,
//       nastiParams = config.nasti,
//       cacheParams = config.cache
//     ),
//     args
//   )
// }

// class MemArbiterIO(params: NastiBundleParameters) extends Bundle {
//   val icache = Flipped(new NastiBundle(params))
//   val dcache = Flipped(new NastiBundle(params))
//   val nasti = new NastiBundle(params)
// }

// object MemArbiterState extends ChiselEnum {
//   val sIdle, sICacheRead, sDCacheRead, sDCacheWrite, sDCacheAck = Value
// }

// class MemArbiter(params: NastiBundleParameters) extends Module {
//   val io = IO(new MemArbiterIO(params))

//   import MemArbiterState._
//   val state = RegInit(sIdle)

//   // Write Address
//   io.nasti.aw.bits := io.dcache.aw.bits
//   io.nasti.aw.valid := io.dcache.aw.valid && state === sIdle
//   io.dcache.aw.ready := io.nasti.aw.ready && state === sIdle
//   io.icache.aw := DontCare

//   // Write Data
//   io.nasti.w.bits := io.dcache.w.bits
//   io.nasti.w.valid := io.dcache.w.valid && state === sDCacheWrite
//   io.dcache.w.ready := io.nasti.w.ready && state === sDCacheWrite
//   io.icache.w := DontCare

//   // Write Ack
//   io.dcache.b.bits := io.nasti.b.bits
//   io.dcache.b.valid := io.nasti.b.valid && state === sDCacheAck
//   io.nasti.b.ready := io.dcache.b.ready && state === sDCacheAck
//   io.icache.b := DontCare

//   // Read Address
//   io.nasti.ar.bits := NastiAddressBundle(params)(
//     Mux(io.dcache.ar.valid, io.dcache.ar.bits.id, io.icache.ar.bits.id),
//     Mux(io.dcache.ar.valid, io.dcache.ar.bits.addr, io.icache.ar.bits.addr),
//     Mux(io.dcache.ar.valid, io.dcache.ar.bits.size, io.icache.ar.bits.size),
//     Mux(io.dcache.ar.valid, io.dcache.ar.bits.len, io.icache.ar.bits.len)
//   )
//   io.nasti.ar.valid := (io.icache.ar.valid || io.dcache.ar.valid) &&
//     !io.nasti.aw.valid && state === sIdle
//   io.dcache.ar.ready := io.nasti.ar.ready && !io.nasti.aw.valid && state === sIdle
//   io.icache.ar.ready := io.dcache.ar.ready && !io.dcache.ar.valid

//   // Read Data
//   io.icache.r.bits := io.nasti.r.bits
//   io.dcache.r.bits := io.nasti.r.bits
//   io.icache.r.valid := io.nasti.r.valid && state === sICacheRead
//   io.dcache.r.valid := io.nasti.r.valid && state === sDCacheRead
//   io.nasti.r.ready := io.icache.r.ready && state === sICacheRead ||
//     io.dcache.r.ready && state === sDCacheRead

//   switch(state) {
//     is(sIdle) {
//       when(io.dcache.aw.fire) {
//         state := sDCacheWrite
//       }.elsewhen(io.dcache.ar.fire) {
//         state := sDCacheRead
//       }.elsewhen(io.icache.ar.fire) {
//         state := sICacheRead
//       }
//     }
//     is(sICacheRead) {
//       when(io.nasti.r.fire && io.nasti.r.bits.last) {
//         state := sIdle
//       }
//     }
//     is(sDCacheRead) {
//       when(io.nasti.r.fire && io.nasti.r.bits.last) {
//         state := sIdle
//       }
//     }
//     is(sDCacheWrite) {
//       when(io.dcache.w.fire && io.dcache.w.bits.last) {
//         state := sDCacheAck
//       }
//     }
//     is(sDCacheAck) {
//       when(io.nasti.b.fire) {
//         state := sIdle
//       }
//     }
//   }
// }

// class TileIO(xlen: Int, nastiParams: NastiBundleParameters) extends Bundle {
//   val host = new HostIO(xlen)
//   val nasti = new NastiBundle(nastiParams)
// }

// object Tile {
//   def apply(config: Config): Tile = new Tile(config.core, config.nasti, config.cache)
// }

// class Tile(val coreParams: CoreConfig, val nastiParams: NastiBundleParameters, val cacheParams: CacheConfig)
//     extends Module {
//   val io = IO(new TileIO(coreParams.xlen, nastiParams))
//   val core = Module(new Core(coreParams))
//   val icache = Module(new Cache(cacheParams, nastiParams, coreParams.xlen))
//   val dcache = Module(new Cache(cacheParams, nastiParams, coreParams.xlen))
//   val arb = Module(new MemArbiter(nastiParams))

//   io.host <> core.io.host
//   core.io.icache <> icache.io.cpu
//   core.io.dcache <> dcache.io.cpu
//   arb.io.icache <> icache.io.nasti
//   arb.io.dcache <> dcache.io.nasti
//   io.nasti <> arb.io.nasti
// }


// object Instructions {
//   // Loads
//   def LB = BitPat("b?????????????????000?????0000011")
//   def LH = BitPat("b?????????????????001?????0000011")
//   def LW = BitPat("b?????????????????010?????0000011")
//   def LBU = BitPat("b?????????????????100?????0000011")
//   def LHU = BitPat("b?????????????????101?????0000011")
//   // Stores
//   def SB = BitPat("b?????????????????000?????0100011")
//   def SH = BitPat("b?????????????????001?????0100011")
//   def SW = BitPat("b?????????????????010?????0100011")
//   // Shifts
//   def SLL = BitPat("b0000000??????????001?????0110011")
//   def SLLI = BitPat("b0000000??????????001?????0010011")
//   def SRL = BitPat("b0000000??????????101?????0110011")
//   def SRLI = BitPat("b0000000??????????101?????0010011")
//   def SRA = BitPat("b0100000??????????101?????0110011")
//   def SRAI = BitPat("b0100000??????????101?????0010011")
//   // Arithmetic
//   def ADD = BitPat("b0000000??????????000?????0110011")
//   def ADDI = BitPat("b?????????????????000?????0010011")
//   def SUB = BitPat("b0100000??????????000?????0110011")
//   def LUI = BitPat("b?????????????????????????0110111")
//   def AUIPC = BitPat("b?????????????????????????0010111")
//   // Logical
//   def XOR = BitPat("b0000000??????????100?????0110011")
//   def XORI = BitPat("b?????????????????100?????0010011")
//   def OR = BitPat("b0000000??????????110?????0110011")
//   def ORI = BitPat("b?????????????????110?????0010011")
//   def AND = BitPat("b0000000??????????111?????0110011")
//   def ANDI = BitPat("b?????????????????111?????0010011")
//   // Compare
//   def SLT = BitPat("b0000000??????????010?????0110011")
//   def SLTI = BitPat("b?????????????????010?????0010011")
//   def SLTU = BitPat("b0000000??????????011?????0110011")
//   def SLTIU = BitPat("b?????????????????011?????0010011")
//   // Branches
//   def BEQ = BitPat("b?????????????????000?????1100011")
//   def BNE = BitPat("b?????????????????001?????1100011")
//   def BLT = BitPat("b?????????????????100?????1100011")
//   def BGE = BitPat("b?????????????????101?????1100011")
//   def BLTU = BitPat("b?????????????????110?????1100011")
//   def BGEU = BitPat("b?????????????????111?????1100011")
//   // Jump & Link
//   def JAL = BitPat("b?????????????????????????1101111")
//   def JALR = BitPat("b?????????????????000?????1100111")
//   // Synch
//   def FENCE = BitPat("b0000????????00000000000000001111")
//   def FENCEI = BitPat("b00000000000000000001000000001111")
//   // CSR Access
//   def CSRRW = BitPat("b?????????????????001?????1110011")
//   def CSRRS = BitPat("b?????????????????010?????1110011")
//   def CSRRC = BitPat("b?????????????????011?????1110011")
//   def CSRRWI = BitPat("b?????????????????101?????1110011")
//   def CSRRSI = BitPat("b?????????????????110?????1110011")
//   def CSRRCI = BitPat("b?????????????????111?????1110011")
//   // Change Level
//   def ECALL = BitPat("b00000000000000000000000001110011")
//   def EBREAK = BitPat("b00000000000100000000000001110011")
//   def ERET = BitPat("b00010000000000000000000001110011")
//   def WFI = BitPat("b00010000001000000000000001110011")

//   def NOP = BitPat.bitPatToUInt(BitPat("b00000000000000000000000000010011"))
// }

// class ImmGenIO(xlen: Int) extends Bundle {
//   val inst = Input(UInt(xlen.W))
//   val sel = Input(UInt(3.W))
//   val out = Output(UInt(xlen.W))
// }

// trait ImmGen extends Module {
//   def xlen: Int
//   val io: ImmGenIO
// }

// class ImmGenWire(val xlen: Int) extends ImmGen {
//   val io = IO(new ImmGenIO(xlen))
//   val Iimm = io.inst(31, 20).asSInt
//   val Simm = Cat(io.inst(31, 25), io.inst(11, 7)).asSInt
//   val Bimm = Cat(io.inst(31), io.inst(7), io.inst(30, 25), io.inst(11, 8), 0.U(1.W)).asSInt
//   val Uimm = Cat(io.inst(31, 12), 0.U(12.W)).asSInt
//   val Jimm = Cat(io.inst(31), io.inst(19, 12), io.inst(20), io.inst(30, 25), io.inst(24, 21), 0.U(1.W)).asSInt
//   val Zimm = io.inst(19, 15).zext

//   io.out := MuxLookup(io.sel, Iimm & (-2).S, (
//     Seq(IMM_I -> Iimm, IMM_S -> Simm, IMM_B -> Bimm, IMM_U -> Uimm, IMM_J -> Jimm, IMM_Z -> Zimm)
//   )).asUInt
// }

// class ImmGenMux(val xlen: Int) extends ImmGen {
//   val io = IO(new ImmGenIO(xlen))
//   val sign = Mux(io.sel === IMM_Z, 0.S, io.inst(31).asSInt)
//   val b30_20 = Mux(io.sel === IMM_U, io.inst(30, 20).asSInt, sign)
//   val b19_12 = Mux(io.sel =/= IMM_U && io.sel =/= IMM_J, sign, io.inst(19, 12).asSInt)
//   val b11 = Mux(
//     io.sel === IMM_U || io.sel === IMM_Z,
//     0.S,
//     Mux(io.sel === IMM_J, io.inst(20).asSInt, Mux(io.sel === IMM_B, io.inst(7).asSInt, sign))
//   )
//   val b10_5 = Mux(io.sel === IMM_U || io.sel === IMM_Z, 0.U, io.inst(30, 25))
//   val b4_1 = Mux(
//     io.sel === IMM_U,
//     0.U,
//     Mux(io.sel === IMM_S || io.sel === IMM_B, io.inst(11, 8), Mux(io.sel === IMM_Z, io.inst(19, 16), io.inst(24, 21)))
//   )
//   val b0 =
//     Mux(io.sel === IMM_S, io.inst(7), Mux(io.sel === IMM_I, io.inst(20), Mux(io.sel === IMM_Z, io.inst(15), 0.U)))

//   io.out := Cat(sign, b30_20, b19_12, b11, b10_5, b4_1, b0).asSInt.asUInt
// }

// // See LICENSE for license details.



// object Consts {
//   val PC_START = 0x200
//   val PC_EVEC = 0x100
// }

// class DatapathIO(xlen: Int) extends Bundle {
//   val host = new HostIO(xlen)
//   val icache = Flipped(new CacheIO(xlen, xlen))
//   val dcache = Flipped(new CacheIO(xlen, xlen))
//   val ctrl = Flipped(new ControlSignals)
// }

// class FetchExecutePipelineRegister(xlen: Int) extends Bundle {
//   val inst = chiselTypeOf(Instructions.NOP)
//   val pc = UInt(xlen.W)
// }

// class ExecuteWritebackPipelineRegister(xlen: Int) extends Bundle {
//   val inst = chiselTypeOf(Instructions.NOP)
//   val pc = UInt(xlen.W)
//   val alu = UInt(xlen.W)
//   val csr_in = UInt(xlen.W)
// }

// class Datapath(val conf: CoreConfig) extends Module {
//   val io = IO(new DatapathIO(conf.xlen))
//   val csr = Module(new CSR(conf.xlen))
//   val regFile = Module(new RegFile(conf.xlen))
//   val alu = Module(conf.makeAlu(conf.xlen))
//   val immGen = Module(conf.makeImmGen(conf.xlen))
//   val brCond = Module(conf.makeBrCond(conf.xlen))

//   import Control._

//   /** Pipeline State Registers * */

//   /** *** Fetch / Execute Registers ****
//     */
//   val fe_reg = RegInit(
//     (new FetchExecutePipelineRegister(conf.xlen)).Lit(
//       _.inst -> Instructions.NOP,
//       _.pc -> 0.U
//     )
//   )

//   /** *** Execute / Write Back Registers ****
//     */
//   val ew_reg = RegInit(
//     (new ExecuteWritebackPipelineRegister(conf.xlen)).Lit(
//       _.inst -> Instructions.NOP,
//       _.pc -> 0.U,
//       _.alu -> 0.U,
//       _.csr_in -> 0.U
//     )
//   )

//   /** **** Control signals ****
//     */
//   val st_type = Reg(io.ctrl.st_type.cloneType)
//   val ld_type = Reg(io.ctrl.ld_type.cloneType)
//   val wb_sel = Reg(io.ctrl.wb_sel.cloneType)
//   val wb_en = Reg(Bool())
//   val csr_cmd = Reg(io.ctrl.csr_cmd.cloneType)
//   val illegal = Reg(Bool())
//   val pc_check = Reg(Bool())

//   /** **** Fetch ****
//     */
//   val started = RegNext(reset.asBool)
//   val stall = !io.icache.resp.valid || !io.dcache.resp.valid
//   val pc = RegInit(Consts.PC_START.U(conf.xlen.W) - 4.U(conf.xlen.W))
//   // Next Program Counter
//   val next_pc = MuxCase(
//     pc + 4.U,
//     IndexedSeq(
//       stall -> pc,
//       csr.io.expt -> csr.io.evec,
//       (io.ctrl.pc_sel === PC_EPC) -> csr.io.epc,
//       ((io.ctrl.pc_sel === PC_ALU) || (brCond.io.taken)) -> (alu.io.sum >> 1.U << 1.U),
//       (io.ctrl.pc_sel === PC_0) -> pc
//     )
//   )
//   val inst =
//     Mux(started || io.ctrl.inst_kill || brCond.io.taken || csr.io.expt, Instructions.NOP, io.icache.resp.bits.data)
//   pc := next_pc
//   io.icache.req.bits.addr := next_pc
//   io.icache.req.bits.data := 0.U
//   io.icache.req.bits.mask := 0.U
//   io.icache.req.valid := !stall
//   io.icache.abort := false.B

//   // Pipelining
//   when(!stall) {
//     fe_reg.pc := pc
//     fe_reg.inst := inst
//   }

//   /** **** Execute ****
//     */
//   io.ctrl.inst := fe_reg.inst

//   // regFile read
//   val rd_addr = fe_reg.inst(11, 7)
//   val rs1_addr = fe_reg.inst(19, 15)
//   val rs2_addr = fe_reg.inst(24, 20)
//   regFile.io.raddr1 := rs1_addr
//   regFile.io.raddr2 := rs2_addr

//   // gen immdeates
//   immGen.io.inst := fe_reg.inst
//   immGen.io.sel := io.ctrl.imm_sel

//   // bypass
//   val wb_rd_addr = ew_reg.inst(11, 7)
//   val rs1hazard = wb_en && rs1_addr.orR && (rs1_addr === wb_rd_addr)
//   val rs2hazard = wb_en && rs2_addr.orR && (rs2_addr === wb_rd_addr)
//   val rs1 = Mux(wb_sel === WB_ALU && rs1hazard, ew_reg.alu, regFile.io.rdata1)
//   val rs2 = Mux(wb_sel === WB_ALU && rs2hazard, ew_reg.alu, regFile.io.rdata2)

//   // ALU operations
//   alu.io.A := Mux(io.ctrl.A_sel === A_RS1, rs1, fe_reg.pc)
//   alu.io.B := Mux(io.ctrl.B_sel === B_RS2, rs2, immGen.io.out)
//   alu.io.alu_op := io.ctrl.alu_op

//   // Branch condition calc
//   brCond.io.rs1 := rs1
//   brCond.io.rs2 := rs2
//   brCond.io.br_type := io.ctrl.br_type

//   // D$ access
//   val daddr = Mux(stall, ew_reg.alu, alu.io.sum) >> 2.U << 2.U
//   val woffset = (alu.io.sum(1) << 4.U).asUInt | (alu.io.sum(0) << 3.U).asUInt
//   io.dcache.req.valid := !stall && (io.ctrl.st_type.orR || io.ctrl.ld_type.orR)
//   io.dcache.req.bits.addr := daddr
//   io.dcache.req.bits.data := rs2 << woffset
//   io.dcache.req.bits.mask := MuxLookup(Mux(stall, st_type, io.ctrl.st_type), "b0000".U, (
//     Seq(ST_SW -> "b1111".U, ST_SH -> ("b11".U << alu.io.sum(1, 0)), ST_SB -> ("b1".U << alu.io.sum(1, 0)))
//   ))

//   // Pipelining
//   when(reset.asBool || !stall && csr.io.expt) {
//     st_type := 0.U
//     ld_type := 0.U
//     wb_en := false.B
//     csr_cmd := 0.U
//     illegal := false.B
//     pc_check := false.B
//   }.elsewhen(!stall && !csr.io.expt) {
//     ew_reg.pc := fe_reg.pc
//     ew_reg.inst := fe_reg.inst
//     ew_reg.alu := alu.io.out
//     ew_reg.csr_in := Mux(io.ctrl.imm_sel === IMM_Z, immGen.io.out, rs1)
//     st_type := io.ctrl.st_type
//     ld_type := io.ctrl.ld_type
//     wb_sel := io.ctrl.wb_sel
//     wb_en := io.ctrl.wb_en
//     csr_cmd := io.ctrl.csr_cmd
//     illegal := io.ctrl.illegal
//     pc_check := io.ctrl.pc_sel === PC_ALU
//   }

//   // Load
//   val loffset = (ew_reg.alu(1) << 4.U).asUInt | (ew_reg.alu(0) << 3.U).asUInt
//   val lshift = io.dcache.resp.bits.data >> loffset
//   val load = MuxLookup(ld_type, io.dcache.resp.bits.data.zext, (
//     Seq(
//       LD_LH -> lshift(15, 0).asSInt,
//       LD_LB -> lshift(7, 0).asSInt,
//       LD_LHU -> lshift(15, 0).zext,
//       LD_LBU -> lshift(7, 0).zext
//     )
//   ))

//   // CSR access
//   csr.io.stall := stall
//   csr.io.in := ew_reg.csr_in
//   csr.io.cmd := csr_cmd
//   csr.io.inst := ew_reg.inst
//   csr.io.pc := ew_reg.pc
//   csr.io.addr := ew_reg.alu
//   csr.io.illegal := illegal
//   csr.io.pc_check := pc_check
//   csr.io.ld_type := ld_type
//   csr.io.st_type := st_type
//   io.host <> csr.io.host

//   // Regfile Write
//   val regWrite =
//     MuxLookup(wb_sel, ew_reg.alu.zext, (
//       Seq(WB_MEM -> load, WB_PC4 -> (ew_reg.pc + 4.U).zext, WB_CSR -> csr.io.out.zext)
//     )).asUInt

//   regFile.io.wen := wb_en && !stall && !csr.io.expt
//   regFile.io.waddr := wb_rd_addr
//   regFile.io.wdata := regWrite

//   // Abort store when there's an excpetion
//   io.dcache.abort := csr.io.expt
//   // assume(!io.dcache.abort)
//   // TODO: re-enable through AOP
// //  if (p(Trace)) {
// //    printf(
// //      "PC: %x, INST: %x, REG[%d] <- %x\n",
// //      ew_reg.pc,
// //      ew_reg.inst,
// //      Mux(regFile.io.wen, wb_rd_addr, 0.U),
// //      Mux(regFile.io.wen, regFile.io.wdata, 0.U)
// //    )
// //  }
// }

// // See LICENSE for license details.

// object CSR {
//   val N = 0.U(3.W)
//   val W = 1.U(3.W)
//   val S = 2.U(3.W)
//   val C = 3.U(3.W)
//   val P = 4.U(3.W)

//   // Supports machine & user modes
//   val PRV_U = 0x0.U(2.W)
//   val PRV_M = 0x3.U(2.W)

//   // User-level CSR addrs
//   val cycle = 0xc00.U(12.W)
//   val time = 0xc01.U(12.W)
//   val instret = 0xc02.U(12.W)
//   val cycleh = 0xc80.U(12.W)
//   val timeh = 0xc81.U(12.W)
//   val instreth = 0xc82.U(12.W)

//   // Supervisor-level CSR addrs
//   val cyclew = 0x900.U(12.W)
//   val timew = 0x901.U(12.W)
//   val instretw = 0x902.U(12.W)
//   val cyclehw = 0x980.U(12.W)
//   val timehw = 0x981.U(12.W)
//   val instrethw = 0x982.U(12.W)

//   // Machine-level CSR addrs
//   // Machine Information Registers
//   val mcpuid = 0xf00.U(12.W)
//   val mimpid = 0xf01.U(12.W)
//   val mhartid = 0xf10.U(12.W)
//   // Machine Trap Setup
//   val mstatus = 0x300.U(12.W)
//   val mtvec = 0x301.U(12.W)
//   val mtdeleg = 0x302.U(12.W)
//   val mie = 0x304.U(12.W)
//   val mtimecmp = 0x321.U(12.W)
//   // Machine Timers and Counters
//   val mtime = 0x701.U(12.W)
//   val mtimeh = 0x741.U(12.W)
//   // Machine Trap Handling
//   val mscratch = 0x340.U(12.W)
//   val mepc = 0x341.U(12.W)
//   val mcause = 0x342.U(12.W)
//   val mbadaddr = 0x343.U(12.W)
//   val mip = 0x344.U(12.W)
//   // Machine HITF
//   val mtohost = 0x780.U(12.W)
//   val mfromhost = 0x781.U(12.W)

//   val regs = List(
//     cycle,
//     time,
//     instret,
//     cycleh,
//     timeh,
//     instreth,
//     cyclew,
//     timew,
//     instretw,
//     cyclehw,
//     timehw,
//     instrethw,
//     mcpuid,
//     mimpid,
//     mhartid,
//     mtvec,
//     mtdeleg,
//     mie,
//     mtimecmp,
//     mtime,
//     mtimeh,
//     mscratch,
//     mepc,
//     mcause,
//     mbadaddr,
//     mip,
//     mtohost,
//     mfromhost,
//     mstatus
//   )
// }

// object Cause {
//   val InstAddrMisaligned = 0x0.U
//   val IllegalInst = 0x2.U
//   val Breakpoint = 0x3.U
//   val LoadAddrMisaligned = 0x4.U
//   val StoreAddrMisaligned = 0x6.U
//   val Ecall = 0x8.U
// }

// class CSRIO(xlen: Int) extends Bundle {
//   val stall = Input(Bool())
//   val cmd = Input(UInt(3.W))
//   val in = Input(UInt(xlen.W))
//   val out = Output(UInt(xlen.W))
//   // Excpetion
//   val pc = Input(UInt(xlen.W))
//   val addr = Input(UInt(xlen.W))
//   val inst = Input(UInt(xlen.W))
//   val illegal = Input(Bool())
//   val st_type = Input(UInt(2.W))
//   val ld_type = Input(UInt(3.W))
//   val pc_check = Input(Bool())
//   val expt = Output(Bool())
//   val evec = Output(UInt(xlen.W))
//   val epc = Output(UInt(xlen.W))
//   // HTIF
//   val host = new HostIO(xlen)
// }

// class CSR(val xlen: Int) extends Module {
//   val io = IO(new CSRIO(xlen))

//   val csr_addr = io.inst(31, 20)
//   val rs1_addr = io.inst(19, 15)

//   // user counters
//   val time = RegInit(0.U(xlen.W))
//   val timeh = RegInit(0.U(xlen.W))
//   val cycle = RegInit(0.U(xlen.W))
//   val cycleh = RegInit(0.U(xlen.W))
//   val instret = RegInit(0.U(xlen.W))
//   val instreth = RegInit(0.U(xlen.W))

//   val mcpuid = Cat(
//     0.U(2.W) /* RV32I */,
//     0.U((xlen - 28).W),
//     (1 << ('I' - 'A') /* Base ISA */ |
//       1 << ('U' - 'A') /* User Mode */ ).U(26.W)
//   )
//   val mimpid = 0.U(xlen.W) // not implemented
//   val mhartid = 0.U(xlen.W) // only one hart

//   // interrupt enable stack
//   val PRV = RegInit(CSR.PRV_M)
//   val PRV1 = RegInit(CSR.PRV_M)
//   val PRV2 = 0.U(2.W)
//   val PRV3 = 0.U(2.W)
//   val IE = RegInit(false.B)
//   val IE1 = RegInit(false.B)
//   val IE2 = false.B
//   val IE3 = false.B
//   // virtualization management field
//   val VM = 0.U(5.W)
//   // memory privilege
//   val MPRV = false.B
//   // extention context status
//   val XS = 0.U(2.W)
//   val FS = 0.U(2.W)
//   val SD = 0.U(1.W)
//   val mstatus = Cat(SD, 0.U((xlen - 23).W), VM, MPRV, XS, FS, PRV3, IE3, PRV2, IE2, PRV1, IE1, PRV, IE)
//   val mtvec = Consts.PC_EVEC.U(xlen.W)
//   val mtdeleg = 0x0.U(xlen.W)

//   // interrupt registers
//   val MTIP = RegInit(false.B)
//   val HTIP = false.B
//   val STIP = false.B
//   val MTIE = RegInit(false.B)
//   val HTIE = false.B
//   val STIE = false.B
//   val MSIP = RegInit(false.B)
//   val HSIP = false.B
//   val SSIP = false.B
//   val MSIE = RegInit(false.B)
//   val HSIE = false.B
//   val SSIE = false.B
//   val mip = Cat(0.U((xlen - 8).W), MTIP, HTIP, STIP, false.B, MSIP, HSIP, SSIP, false.B)
//   val mie = Cat(0.U((xlen - 8).W), MTIE, HTIE, STIE, false.B, MSIE, HSIE, SSIE, false.B)

//   val mtimecmp = Reg(UInt(xlen.W))

//   val mscratch = Reg(UInt(xlen.W))

//   val mepc = Reg(UInt(xlen.W))
//   val mcause = Reg(UInt(xlen.W))
//   val mbadaddr = Reg(UInt(xlen.W))

//   val mtohost = RegInit(0.U(xlen.W))
//   val mfromhost = Reg(UInt(xlen.W))
//   io.host.tohost := mtohost
//   when(io.host.fromhost.valid) {
//     mfromhost := io.host.fromhost.bits
//   }

//   val csrFile = Seq(
//     BitPat(CSR.cycle) -> cycle,
//     BitPat(CSR.time) -> time,
//     BitPat(CSR.instret) -> instret,
//     BitPat(CSR.cycleh) -> cycleh,
//     BitPat(CSR.timeh) -> timeh,
//     BitPat(CSR.instreth) -> instreth,
//     BitPat(CSR.cyclew) -> cycle,
//     BitPat(CSR.timew) -> time,
//     BitPat(CSR.instretw) -> instret,
//     BitPat(CSR.cyclehw) -> cycleh,
//     BitPat(CSR.timehw) -> timeh,
//     BitPat(CSR.instrethw) -> instreth,
//     BitPat(CSR.mcpuid) -> mcpuid,
//     BitPat(CSR.mimpid) -> mimpid,
//     BitPat(CSR.mhartid) -> mhartid,
//     BitPat(CSR.mtvec) -> mtvec,
//     BitPat(CSR.mtdeleg) -> mtdeleg,
//     BitPat(CSR.mie) -> mie,
//     BitPat(CSR.mtimecmp) -> mtimecmp,
//     BitPat(CSR.mtime) -> time,
//     BitPat(CSR.mtimeh) -> timeh,
//     BitPat(CSR.mscratch) -> mscratch,
//     BitPat(CSR.mepc) -> mepc,
//     BitPat(CSR.mcause) -> mcause,
//     BitPat(CSR.mbadaddr) -> mbadaddr,
//     BitPat(CSR.mip) -> mip,
//     BitPat(CSR.mtohost) -> mtohost,
//     BitPat(CSR.mfromhost) -> mfromhost,
//     BitPat(CSR.mstatus) -> mstatus
//   )

//   io.out := Lookup(csr_addr, 0.U, csrFile).asUInt

//   val privValid = csr_addr(9, 8) <= PRV
//   val privInst = io.cmd === CSR.P
//   val isEcall = privInst && !csr_addr(0) && !csr_addr(8)
//   val isEbreak = privInst && csr_addr(0) && !csr_addr(8)
//   val isEret = privInst && !csr_addr(0) && csr_addr(8)
//   val csrValid = csrFile.map(_._1 === csr_addr).reduce(_ || _)
//   val csrRO = csr_addr(11, 10).andR || csr_addr === CSR.mtvec || csr_addr === CSR.mtdeleg
//   val wen = io.cmd === CSR.W || io.cmd(1) && rs1_addr.orR
//   val wdata = MuxLookup(io.cmd, 0.U, (
//     Seq(
//       CSR.W -> io.in,
//       CSR.S -> (io.out | io.in),
//       CSR.C -> (io.out & ~io.in)
//     )
//   ))
//   val iaddrInvalid = io.pc_check && io.addr(1)
//   val laddrInvalid = MuxLookup(io.ld_type, false.B, (
//     Seq(Control.LD_LW -> io.addr(1, 0).orR, Control.LD_LH -> io.addr(0), Control.LD_LHU -> io.addr(0))
//   ))
//   val saddrInvalid =
//     MuxLookup(io.st_type, false.B, (Seq(Control.ST_SW -> io.addr(1, 0).orR, Control.ST_SH -> io.addr(0))))
//   io.expt := io.illegal || iaddrInvalid || laddrInvalid || saddrInvalid ||
//     io.cmd(1, 0).orR && (!csrValid || !privValid) || wen && csrRO ||
//     (privInst && !privValid) || isEcall || isEbreak
//   io.evec := mtvec + (PRV << 6)
//   io.epc := mepc

//   // Counters
//   time := time + 1.U
//   when(time.andR) { timeh := timeh + 1.U }
//   cycle := cycle + 1.U
//   when(cycle.andR) { cycleh := cycleh + 1.U }
//   val isInstRet = io.inst =/= Instructions.NOP && (!io.expt || isEcall || isEbreak) && !io.stall
//   when(isInstRet) { instret := instret + 1.U }
//   when(isInstRet && instret.andR) { instreth := instreth + 1.U }

//   when(!io.stall) {
//     when(io.expt) {
//       mepc := io.pc >> 2 << 2
//       mcause := Mux(
//         iaddrInvalid,
//         Cause.InstAddrMisaligned,
//         Mux(
//           laddrInvalid,
//           Cause.LoadAddrMisaligned,
//           Mux(
//             saddrInvalid,
//             Cause.StoreAddrMisaligned,
//             Mux(isEcall, Cause.Ecall + PRV, Mux(isEbreak, Cause.Breakpoint, Cause.IllegalInst))
//           )
//         )
//       )
//       PRV := CSR.PRV_M
//       IE := false.B
//       PRV1 := PRV
//       IE1 := IE
//       when(iaddrInvalid || laddrInvalid || saddrInvalid) { mbadaddr := io.addr }
//     }.elsewhen(isEret) {
//       PRV := PRV1
//       IE := IE1
//       PRV1 := CSR.PRV_U
//       IE1 := true.B
//     }.elsewhen(wen) {
//       when(csr_addr === CSR.mstatus) {
//         PRV1 := wdata(5, 4)
//         IE1 := wdata(3)
//         PRV := wdata(2, 1)
//         IE := wdata(0)
//       }
//         .elsewhen(csr_addr === CSR.mip) {
//           MTIP := wdata(7)
//           MSIP := wdata(3)
//         }
//         .elsewhen(csr_addr === CSR.mie) {
//           MTIE := wdata(7)
//           MSIE := wdata(3)
//         }
//         .elsewhen(csr_addr === CSR.mtime) { time := wdata }
//         .elsewhen(csr_addr === CSR.mtimeh) { timeh := wdata }
//         .elsewhen(csr_addr === CSR.mtimecmp) { mtimecmp := wdata }
//         .elsewhen(csr_addr === CSR.mscratch) { mscratch := wdata }
//         .elsewhen(csr_addr === CSR.mepc) { mepc := wdata >> 2.U << 2.U }
//         .elsewhen(csr_addr === CSR.mcause) { mcause := wdata & (BigInt(1) << (xlen - 1) | 0xf).U }
//         .elsewhen(csr_addr === CSR.mbadaddr) { mbadaddr := wdata }
//         .elsewhen(csr_addr === CSR.mtohost) { mtohost := wdata }
//         .elsewhen(csr_addr === CSR.mfromhost) { mfromhost := wdata }
//         .elsewhen(csr_addr === CSR.cyclew) { cycle := wdata }
//         .elsewhen(csr_addr === CSR.timew) { time := wdata }
//         .elsewhen(csr_addr === CSR.instretw) { instret := wdata }
//         .elsewhen(csr_addr === CSR.cyclehw) { cycleh := wdata }
//         .elsewhen(csr_addr === CSR.timehw) { timeh := wdata }
//         .elsewhen(csr_addr === CSR.instrethw) { instreth := wdata }
//     }
//   }
// }

// case class CoreConfig(
//   xlen:       Int,
//   makeAlu:    Int => Alu = new AluSimple(_),
//   makeBrCond: Int => BrCond = new BrCondSimple(_),
//   makeImmGen: Int => ImmGen = new ImmGenWire(_))

// class HostIO(xlen: Int) extends Bundle {
//   val fromhost = Flipped(Valid(UInt(xlen.W)))
//   val tohost = Output(UInt(xlen.W))
// }

// class CoreIO(xlen: Int) extends Bundle {
//   val host = new HostIO(xlen)
//   val icache = Flipped(new CacheIO(xlen, xlen))
//   val dcache = Flipped(new CacheIO(xlen, xlen))
// }

// class Core(val conf: CoreConfig) extends Module {
//   val ctrl = Module(new Control)
//  val io = IO(new CoreIO(conf.xlen))
//   val dpath = Module(new Datapath(conf))
 
//   io.host <> dpath.io.host
//   dpath.io.icache <> io.icache
//   dpath.io.dcache <> io.dcache
//   dpath.io.ctrl <> ctrl.io
// }

// object Control {
//   val Y = true.B
//   val N = false.B

//   // pc_sel
//   val PC_4 = 0.U(2.W)
//   val PC_ALU = 1.U(2.W)
//   val PC_0 = 2.U(2.W)
//   val PC_EPC = 3.U(2.W)

//   // A_sel
//   val A_XXX = 0.U(1.W)
//   val A_PC = 0.U(1.W)
//   val A_RS1 = 1.U(1.W)

//   // B_sel
//   val B_XXX = 0.U(1.W)
//   val B_IMM = 0.U(1.W)
//   val B_RS2 = 1.U(1.W)

//   // imm_sel
//   val IMM_X = 0.U(3.W)
//   val IMM_I = 1.U(3.W)
//   val IMM_S = 2.U(3.W)
//   val IMM_U = 3.U(3.W)
//   val IMM_J = 4.U(3.W)
//   val IMM_B = 5.U(3.W)
//   val IMM_Z = 6.U(3.W)

//   // br_type
//   val BR_XXX = 0.U(3.W)
//   val BR_LTU = 1.U(3.W)
//   val BR_LT = 2.U(3.W)
//   val BR_EQ = 3.U(3.W)
//   val BR_GEU = 4.U(3.W)
//   val BR_GE = 5.U(3.W)
//   val BR_NE = 6.U(3.W)

//   // st_type
//   val ST_XXX = 0.U(2.W)
//   val ST_SW = 1.U(2.W)
//   val ST_SH = 2.U(2.W)
//   val ST_SB = 3.U(2.W)

//   // ld_type
//   val LD_XXX = 0.U(3.W)
//   val LD_LW = 1.U(3.W)
//   val LD_LH = 2.U(3.W)
//   val LD_LB = 3.U(3.W)
//   val LD_LHU = 4.U(3.W)
//   val LD_LBU = 5.U(3.W)

//   // wb_sel
//   val WB_ALU = 0.U(2.W)
//   val WB_MEM = 1.U(2.W)
//   val WB_PC4 = 2.U(2.W)
//   val WB_CSR = 3.U(2.W)

//   import Alu._
//   import Instructions._

//   // format: off
//   val default =
//   //                                                              kill                        wb_en  illegal?
//   //             pc_sel  A_sel   B_sel  imm_sel   alu_op   br_type  |  st_type ld_type wb_sel  | csr_cmd |
//   //               |       |       |     |          |          |    |     |       |       |    |  |      |
//              List(PC_4  , A_XXX,  B_XXX, IMM_X, ALU_XXX   , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, N, CSR.N, Y)
//   val map = Array(
//     LUI   -> List(PC_4  , A_PC,   B_IMM, IMM_U, ALU_COPY_B, BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     AUIPC -> List(PC_4  , A_PC,   B_IMM, IMM_U, ALU_ADD   , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     JAL   -> List(PC_ALU, A_PC,   B_IMM, IMM_J, ALU_ADD   , BR_XXX, Y, ST_XXX, LD_XXX, WB_PC4, Y, CSR.N, N),
//     JALR  -> List(PC_ALU, A_RS1,  B_IMM, IMM_I, ALU_ADD   , BR_XXX, Y, ST_XXX, LD_XXX, WB_PC4, Y, CSR.N, N),
//     BEQ   -> List(PC_4  , A_PC,   B_IMM, IMM_B, ALU_ADD   , BR_EQ , N, ST_XXX, LD_XXX, WB_ALU, N, CSR.N, N),
//     BNE   -> List(PC_4  , A_PC,   B_IMM, IMM_B, ALU_ADD   , BR_NE , N, ST_XXX, LD_XXX, WB_ALU, N, CSR.N, N),
//     BLT   -> List(PC_4  , A_PC,   B_IMM, IMM_B, ALU_ADD   , BR_LT , N, ST_XXX, LD_XXX, WB_ALU, N, CSR.N, N),
//     BGE   -> List(PC_4  , A_PC,   B_IMM, IMM_B, ALU_ADD   , BR_GE , N, ST_XXX, LD_XXX, WB_ALU, N, CSR.N, N),
//     BLTU  -> List(PC_4  , A_PC,   B_IMM, IMM_B, ALU_ADD   , BR_LTU, N, ST_XXX, LD_XXX, WB_ALU, N, CSR.N, N),
//     BGEU  -> List(PC_4  , A_PC,   B_IMM, IMM_B, ALU_ADD   , BR_GEU, N, ST_XXX, LD_XXX, WB_ALU, N, CSR.N, N),
//     LB    -> List(PC_0  , A_RS1,  B_IMM, IMM_I, ALU_ADD   , BR_XXX, Y, ST_XXX, LD_LB , WB_MEM, Y, CSR.N, N),
//     LH    -> List(PC_0  , A_RS1,  B_IMM, IMM_I, ALU_ADD   , BR_XXX, Y, ST_XXX, LD_LH , WB_MEM, Y, CSR.N, N),
//     LW    -> List(PC_0  , A_RS1,  B_IMM, IMM_I, ALU_ADD   , BR_XXX, Y, ST_XXX, LD_LW , WB_MEM, Y, CSR.N, N),
//     LBU   -> List(PC_0  , A_RS1,  B_IMM, IMM_I, ALU_ADD   , BR_XXX, Y, ST_XXX, LD_LBU, WB_MEM, Y, CSR.N, N),
//     LHU   -> List(PC_0  , A_RS1,  B_IMM, IMM_I, ALU_ADD   , BR_XXX, Y, ST_XXX, LD_LHU, WB_MEM, Y, CSR.N, N),
//     SB    -> List(PC_4  , A_RS1,  B_IMM, IMM_S, ALU_ADD   , BR_XXX, N, ST_SB , LD_XXX, WB_ALU, N, CSR.N, N),
//     SH    -> List(PC_4  , A_RS1,  B_IMM, IMM_S, ALU_ADD   , BR_XXX, N, ST_SH , LD_XXX, WB_ALU, N, CSR.N, N),
//     SW    -> List(PC_4  , A_RS1,  B_IMM, IMM_S, ALU_ADD   , BR_XXX, N, ST_SW , LD_XXX, WB_ALU, N, CSR.N, N),
//     ADDI  -> List(PC_4  , A_RS1,  B_IMM, IMM_I, ALU_ADD   , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     SLTI  -> List(PC_4  , A_RS1,  B_IMM, IMM_I, ALU_SLT   , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     SLTIU -> List(PC_4  , A_RS1,  B_IMM, IMM_I, ALU_SLTU  , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     XORI  -> List(PC_4  , A_RS1,  B_IMM, IMM_I, ALU_XOR   , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     ORI   -> List(PC_4  , A_RS1,  B_IMM, IMM_I, ALU_OR    , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     ANDI  -> List(PC_4  , A_RS1,  B_IMM, IMM_I, ALU_AND   , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     SLLI  -> List(PC_4  , A_RS1,  B_IMM, IMM_I, ALU_SLL   , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     SRLI  -> List(PC_4  , A_RS1,  B_IMM, IMM_I, ALU_SRL   , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     SRAI  -> List(PC_4  , A_RS1,  B_IMM, IMM_I, ALU_SRA   , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     ADD   -> List(PC_4  , A_RS1,  B_RS2, IMM_X, ALU_ADD   , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     SUB   -> List(PC_4  , A_RS1,  B_RS2, IMM_X, ALU_SUB   , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     SLL   -> List(PC_4  , A_RS1,  B_RS2, IMM_X, ALU_SLL   , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     SLT   -> List(PC_4  , A_RS1,  B_RS2, IMM_X, ALU_SLT   , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     SLTU  -> List(PC_4  , A_RS1,  B_RS2, IMM_X, ALU_SLTU  , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     XOR   -> List(PC_4  , A_RS1,  B_RS2, IMM_X, ALU_XOR   , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     SRL   -> List(PC_4  , A_RS1,  B_RS2, IMM_X, ALU_SRL   , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     SRA   -> List(PC_4  , A_RS1,  B_RS2, IMM_X, ALU_SRA   , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     OR    -> List(PC_4  , A_RS1,  B_RS2, IMM_X, ALU_OR    , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     AND   -> List(PC_4  , A_RS1,  B_RS2, IMM_X, ALU_AND   , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, Y, CSR.N, N),
//     FENCE -> List(PC_4  , A_XXX,  B_XXX, IMM_X, ALU_XXX   , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, N, CSR.N, N),
//     FENCEI-> List(PC_0  , A_XXX,  B_XXX, IMM_X, ALU_XXX   , BR_XXX, Y, ST_XXX, LD_XXX, WB_ALU, N, CSR.N, N),
//     CSRRW -> List(PC_0  , A_RS1,  B_XXX, IMM_X, ALU_COPY_A, BR_XXX, Y, ST_XXX, LD_XXX, WB_CSR, Y, CSR.W, N),
//     CSRRS -> List(PC_0  , A_RS1,  B_XXX, IMM_X, ALU_COPY_A, BR_XXX, Y, ST_XXX, LD_XXX, WB_CSR, Y, CSR.S, N),
//     CSRRC -> List(PC_0  , A_RS1,  B_XXX, IMM_X, ALU_COPY_A, BR_XXX, Y, ST_XXX, LD_XXX, WB_CSR, Y, CSR.C, N),
//     CSRRWI-> List(PC_0  , A_XXX,  B_XXX, IMM_Z, ALU_XXX   , BR_XXX, Y, ST_XXX, LD_XXX, WB_CSR, Y, CSR.W, N),
//     CSRRSI-> List(PC_0  , A_XXX,  B_XXX, IMM_Z, ALU_XXX   , BR_XXX, Y, ST_XXX, LD_XXX, WB_CSR, Y, CSR.S, N),
//     CSRRCI-> List(PC_0  , A_XXX,  B_XXX, IMM_Z, ALU_XXX   , BR_XXX, Y, ST_XXX, LD_XXX, WB_CSR, Y, CSR.C, N),
//     ECALL -> List(PC_4  , A_XXX,  B_XXX, IMM_X, ALU_XXX   , BR_XXX, N, ST_XXX, LD_XXX, WB_CSR, N, CSR.P, N),
//     EBREAK-> List(PC_4  , A_XXX,  B_XXX, IMM_X, ALU_XXX   , BR_XXX, N, ST_XXX, LD_XXX, WB_CSR, N, CSR.P, N),
//     ERET  -> List(PC_EPC, A_XXX,  B_XXX, IMM_X, ALU_XXX   , BR_XXX, Y, ST_XXX, LD_XXX, WB_CSR, N, CSR.P, N),
//     WFI   -> List(PC_4  , A_XXX,  B_XXX, IMM_X, ALU_XXX   , BR_XXX, N, ST_XXX, LD_XXX, WB_ALU, N, CSR.N, N))
//   // format: on
// }

// class ControlSignals extends Bundle {
//   val inst = Input(UInt(32.W))
//   val pc_sel = Output(UInt(2.W))
//   val inst_kill = Output(Bool())
//   val A_sel = Output(UInt(1.W))
//   val B_sel = Output(UInt(1.W))
//   val imm_sel = Output(UInt(3.W))
//   val alu_op = Output(UInt(4.W))
//   val br_type = Output(UInt(3.W))
//   val st_type = Output(UInt(2.W))
//   val ld_type = Output(UInt(3.W))
//   val wb_sel = Output(UInt(2.W))
//   val wb_en = Output(Bool())
//   val csr_cmd = Output(UInt(3.W))
//   val illegal = Output(Bool())
// }

// class Control extends Module {
//   val io = IO(new ControlSignals)
//   val ctrlSignals = ListLookup(io.inst, Control.default, Control.map)

//   // Control signals for Fetch
//   io.pc_sel := ctrlSignals(0)
//   io.inst_kill := ctrlSignals(6).asBool

//   // Control signals for Execute
//   io.A_sel := ctrlSignals(1)
//   io.B_sel := ctrlSignals(2)
//   io.imm_sel := ctrlSignals(3)
//   io.alu_op := ctrlSignals(4)
//   io.br_type := ctrlSignals(5)
//   io.st_type := ctrlSignals(7)

//   // Control signals for Write Back
//   io.ld_type := ctrlSignals(8)
//   io.wb_sel := ctrlSignals(9)
//   io.wb_en := ctrlSignals(10).asBool
//   io.csr_cmd := ctrlSignals(11)
//   io.illegal := ctrlSignals(12)
// }

// case class Config(core: CoreConfig, cache: CacheConfig, nasti: NastiBundleParameters)

// object MiniConfig {
//   def apply(): Config = {
//     val xlen = 32
//     Config(
//       core = CoreConfig(
//         xlen = xlen,
//         makeAlu = new AluArea(_),
//         makeBrCond = new BrCondArea(_),
//         makeImmGen = new ImmGenWire(_)
//       ),
//       cache = CacheConfig(
//         nWays = 1,
//         nSets = 32,
//         blockBytes = 4 * (xlen / 8) // 4 * 32 bits = 16B
//       ),
//       nasti = NastiBundleParameters(
//         addrBits = 32,
//         dataBits = 64,
//         idBits = 5
//       )
//     )
//   }
// }

// class CacheReq(addrWidth: Int, dataWidth: Int) extends Bundle {
//   val addr = UInt(addrWidth.W)
//   val data = UInt(dataWidth.W)
//   val mask = UInt((dataWidth / 8).W)
// }

// class CacheResp(dataWidth: Int) extends Bundle {
//   val data = UInt(dataWidth.W)
// }

// class CacheIO(addrWidth: Int, dataWidth: Int) extends Bundle {
//   val abort = Input(Bool())
//   val req = Flipped(Valid(new CacheReq(addrWidth, dataWidth)))
//   val resp = Valid(new CacheResp(dataWidth))
// }

// class CacheModuleIO(nastiParams: NastiBundleParameters, addrWidth: Int, dataWidth: Int) extends Bundle {
//   val cpu = new CacheIO(addrWidth, dataWidth)
//   val nasti = new NastiBundle(nastiParams)
// }

// case class CacheConfig(nWays: Int, nSets: Int, blockBytes: Int)

// class MetaData(tagLength: Int) extends Bundle {
//   val tag = UInt(tagLength.W)
// }

// object CacheState extends ChiselEnum {
//   val sIdle, sReadCache, sWriteCache, sWriteBack, sWriteAck, sRefillReady, sRefill = Value
// }

// class Cache(val p: CacheConfig, val nasti: NastiBundleParameters, val xlen: Int) extends Module {
//   // local parameters
//   val nSets = p.nSets
//   val bBytes = p.blockBytes
//   val bBits = bBytes << 3
//   val blen = log2Ceil(bBytes)
//   val slen = log2Ceil(nSets)
//   val tlen = xlen - (slen + blen)
//   val nWords = bBits / xlen
//   val wBytes = xlen / 8
//   val byteOffsetBits = log2Ceil(wBytes)
//   val dataBeats = bBits / nasti.dataBits

//   val io = IO(new CacheModuleIO(nasti, addrWidth = xlen, dataWidth = xlen))

//   // cache states
//   import CacheState._
//   val state = RegInit(sIdle)
//   // memory
//   val v = RegInit(0.U(nSets.W))
//   val d = RegInit(0.U(nSets.W))
//   val metaMem = SyncReadMem(nSets, new MetaData(tlen))
//   val dataMem = Seq.fill(nWords)(SyncReadMem(nSets, Vec(wBytes, UInt(8.W))))

//   val addr_reg = Reg(chiselTypeOf(io.cpu.req.bits.addr))
//   val cpu_data = Reg(chiselTypeOf(io.cpu.req.bits.data))
//   val cpu_mask = Reg(chiselTypeOf(io.cpu.req.bits.mask))

//   // Counters
//   require(dataBeats > 0)
//   val (read_count, read_wrap_out) = Counter(io.nasti.r.fire, dataBeats)
//   val (write_count, write_wrap_out) = Counter(io.nasti.w.fire, dataBeats)

//   val is_idle = state === sIdle
//   val is_read = state === sReadCache
//   val is_write = state === sWriteCache
//   val is_alloc = state === sRefill && read_wrap_out
//   val is_alloc_reg = RegNext(is_alloc)

//   val hit = Wire(Bool())
//   val wen = is_write && (hit || is_alloc_reg) && !io.cpu.abort || is_alloc
//   val ren = !wen && (is_idle || is_read) && io.cpu.req.valid
//   val ren_reg = RegNext(ren)

//   val addr = io.cpu.req.bits.addr
//   val idx = addr(slen + blen - 1, blen)
//   val tag_reg = addr_reg(xlen - 1, slen + blen)
//   val idx_reg = addr_reg(slen + blen - 1, blen)
//   val off_reg = addr_reg(blen - 1, byteOffsetBits)

//   val rmeta = metaMem.read(idx, ren_reg)
//   val rdata = Cat((dataMem.map(_.read(idx, ren_reg).asUInt)).reverse)
//   val rdata_buf = RegEnable(rdata, ren_reg)
//   val refill_buf = Reg(Vec(dataBeats, UInt(nasti.dataBits.W)))
//   val read = Mux(is_alloc_reg, refill_buf.asUInt, Mux(ren_reg, rdata, rdata_buf))

//   hit := v(idx_reg) && rmeta.tag === tag_reg

//   // Read Mux
//   io.cpu.resp.bits.data := VecInit.tabulate(nWords)(i => read((i + 1) * xlen - 1, i * xlen))(off_reg)
//   io.cpu.resp.valid := is_idle || is_read && hit || is_alloc_reg && !cpu_mask.orR

//   when(io.cpu.resp.valid) {
//     addr_reg := addr
//     cpu_data := io.cpu.req.bits.data
//     cpu_mask := io.cpu.req.bits.mask
//   }

//   val wmeta = Wire(new MetaData(tlen))
//   wmeta.tag := tag_reg

//   val wmask = Mux(!is_alloc, (cpu_mask << Cat(off_reg, 0.U(byteOffsetBits.W))).zext, (-1).S)
//   val wdata = Mux(
//     !is_alloc,
//     Fill(nWords, cpu_data),
//     if (refill_buf.size == 1) io.nasti.r.bits.data
//     else Cat(io.nasti.r.bits.data, Cat(refill_buf.init.reverse))
//   )
//   when(wen) {
//     v := v.bitSet(idx_reg, true.B)
//     d := d.bitSet(idx_reg, !is_alloc)
//     when(is_alloc) {
//       metaMem.write(idx_reg, wmeta)
//     }
//     dataMem.zipWithIndex.foreach {
//       case (mem, i) =>
//         val data = VecInit.tabulate(wBytes)(k => wdata(i * xlen + (k + 1) * 8 - 1, i * xlen + k * 8))
//         mem.write(idx_reg, data, wmask((i + 1) * wBytes - 1, i * wBytes).asBools)
//         mem.suggestName(s"dataMem_${i}")
//     }
//   }

//   io.nasti.ar.bits := NastiAddressBundle(nasti)(
//     0.U,
//     (Cat(tag_reg, idx_reg) << blen.U).asUInt,
//     log2Up(nasti.dataBits / 8).U,
//     (dataBeats - 1).U
//   )
//   io.nasti.ar.valid := false.B
//   // read data
//   io.nasti.r.ready := state === sRefill
//   when(io.nasti.r.fire) {
//     refill_buf(read_count) := io.nasti.r.bits.data
//   }

//   // write addr
//   io.nasti.aw.bits := NastiAddressBundle(nasti)(
//     0.U,
//     (Cat(rmeta.tag, idx_reg) << blen.U).asUInt,
//     log2Up(nasti.dataBits / 8).U,
//     (dataBeats - 1).U
//   )
//   io.nasti.aw.valid := false.B
//   // write data
//   io.nasti.w.bits := NastiWriteDataBundle(nasti)(
//     VecInit.tabulate(dataBeats)(i => read((i + 1) * nasti.dataBits - 1, i * nasti.dataBits))(write_count),
//     None,
//     write_wrap_out
//   )
//   io.nasti.w.valid := false.B
//   // write resp
//   io.nasti.b.ready := false.B

//   // Cache FSM
//   val is_dirty = v(idx_reg) && d(idx_reg)
//   switch(state) {
//     is(sIdle) {
//       when(io.cpu.req.valid) {
//         state := Mux(io.cpu.req.bits.mask.orR, sWriteCache, sReadCache)
//       }
//     }
//     is(sReadCache) {
//       when(hit) {
//         when(io.cpu.req.valid) {
//           state := Mux(io.cpu.req.bits.mask.orR, sWriteCache, sReadCache)
//         }.otherwise {
//           state := sIdle
//         }
//       }.otherwise {
//         io.nasti.aw.valid := is_dirty
//         io.nasti.ar.valid := !is_dirty
//         when(io.nasti.aw.fire) {
//           state := sWriteBack
//         }.elsewhen(io.nasti.ar.fire) {
//           state := sRefill
//         }
//       }
//     }
//     is(sWriteCache) {
//       when(hit || is_alloc_reg || io.cpu.abort) {
//         state := sIdle
//       }.otherwise {
//         io.nasti.aw.valid := is_dirty
//         io.nasti.ar.valid := !is_dirty
//         when(io.nasti.aw.fire) {
//           state := sWriteBack
//         }.elsewhen(io.nasti.ar.fire) {
//           state := sRefill
//         }
//       }
//     }
//     is(sWriteBack) {
//       io.nasti.w.valid := true.B
//       when(write_wrap_out) {
//         state := sWriteAck
//       }
//     }
//     is(sWriteAck) {
//       io.nasti.b.ready := true.B
//       when(io.nasti.b.fire) {
//         state := sRefillReady
//       }
//     }
//     is(sRefillReady) {
//       io.nasti.ar.valid := true.B
//       when(io.nasti.ar.fire) {
//         state := sRefill
//       }
//     }
//     is(sRefill) {
//       when(read_wrap_out) {
//         state := Mux(cpu_mask.orR, sWriteCache, sIdle)
//       }
//     }
//   }
// }

// class BrCondIO(xlen: Int) extends Bundle {
//   val rs1 = Input(UInt(xlen.W))
//   val rs2 = Input(UInt(xlen.W))
//   val br_type = Input(UInt(3.W))
//   val taken = Output(Bool())
// }

// trait BrCond extends Module {
//   def xlen: Int
//   val io: BrCondIO
// }

// class BrCondSimple(val xlen: Int) extends BrCond {
//   val io = IO(new BrCondIO(xlen))
//   val eq = io.rs1 === io.rs2
//   val neq = !eq
//   val lt = io.rs1.asSInt < io.rs2.asSInt
//   val ge = !lt
//   val ltu = io.rs1 < io.rs2
//   val geu = !ltu
//   io.taken :=
//     ((io.br_type === BR_EQ) && eq) ||
//       ((io.br_type === BR_NE) && neq) ||
//       ((io.br_type === BR_LT) && lt) ||
//       ((io.br_type === BR_GE) && ge) ||
//       ((io.br_type === BR_LTU) && ltu) ||
//       ((io.br_type === BR_GEU) && geu)
// }

// class BrCondArea(val xlen: Int) extends BrCond {
//   val io = IO(new BrCondIO(xlen))
//   val diff = io.rs1 - io.rs2
//   val neq = diff.orR
//   val eq = !neq
//   val isSameSign = io.rs1(xlen - 1) === io.rs2(xlen - 1)
//   val lt = Mux(isSameSign, diff(xlen - 1), io.rs1(xlen - 1))
//   val ltu = Mux(isSameSign, diff(xlen - 1), io.rs2(xlen - 1))
//   val ge = !lt
//   val geu = !ltu
//   io.taken :=
//     ((io.br_type === BR_EQ) && eq) ||
//       ((io.br_type === BR_NE) && neq) ||
//       ((io.br_type === BR_LT) && lt) ||
//       ((io.br_type === BR_GE) && ge) ||
//       ((io.br_type === BR_LTU) && ltu) ||
//       ((io.br_type === BR_GEU) && geu)
// }

// object Alu {
//   val ALU_ADD = 0.U(4.W)
//   val ALU_SUB = 1.U(4.W)
//   val ALU_AND = 2.U(4.W)
//   val ALU_OR = 3.U(4.W)
//   val ALU_XOR = 4.U(4.W)
//   val ALU_SLT = 5.U(4.W)
//   val ALU_SLL = 6.U(4.W)
//   val ALU_SLTU = 7.U(4.W)
//   val ALU_SRL = 8.U(4.W)
//   val ALU_SRA = 9.U(4.W)
//   val ALU_COPY_A = 10.U(4.W)
//   val ALU_COPY_B = 11.U(4.W)
//   val ALU_XXX = 15.U(4.W)
// }

// class AluIO(width: Int) extends Bundle {
//   val A = Input(UInt(width.W))
//   val B = Input(UInt(width.W))
//   val alu_op = Input(UInt(4.W))
//   val out = Output(UInt(width.W))
//   val sum = Output(UInt(width.W))
// }

// import mini.Alu._

// trait Alu extends Module {
//   def width: Int
//   val io: AluIO
// }

// class AluSimple(val width: Int) extends Alu {
//   val io = IO(new AluIO(width))

//   val shamt = io.B(4, 0).asUInt

//   io.out := MuxLookup(io.alu_op, io.B, (
//     Seq(
//       ALU_ADD -> (io.A + io.B),
//       ALU_SUB -> (io.A - io.B),
//       ALU_SRA -> (io.A.asSInt >> shamt).asUInt,
//       ALU_SRL -> (io.A >> shamt),
//       ALU_SLL -> (io.A << shamt),
//       ALU_SLT -> (io.A.asSInt < io.B.asSInt),
//       ALU_SLTU -> (io.A < io.B),
//       ALU_AND -> (io.A & io.B),
//       ALU_OR -> (io.A | io.B),
//       ALU_XOR -> (io.A ^ io.B),
//       ALU_COPY_A -> io.A
//     )
//   ))

//   io.sum := io.A + Mux(io.alu_op(0), -io.B, io.B)
// }

// class AluArea(val width: Int) extends Alu {
//   val io = IO(new AluIO(width))
//   val sum = io.A + Mux(io.alu_op(0), -io.B, io.B)
//   val cmp =
//     Mux(io.A(width - 1) === io.B(width - 1), sum(width - 1), Mux(io.alu_op(1), io.B(width - 1), io.A(width - 1)))
//   val shamt = io.B(4, 0).asUInt
//   val shin = Mux(io.alu_op(3), io.A, Reverse(io.A))
//   val shiftr = (Cat(io.alu_op(0) && shin(width - 1), shin).asSInt >> shamt)(width - 1, 0)
//   val shiftl = Reverse(shiftr)

//   val out =
//     Mux(
//       io.alu_op === ALU_ADD || io.alu_op === ALU_SUB,
//       sum,
//       Mux(
//         io.alu_op === ALU_SLT || io.alu_op === ALU_SLTU,
//         cmp,
//         Mux(
//           io.alu_op === ALU_SRA || io.alu_op === ALU_SRL,
//           shiftr,
//           Mux(
//             io.alu_op === ALU_SLL,
//             shiftl,
//             Mux(
//               io.alu_op === ALU_AND,
//               io.A & io.B,
//               Mux(
//                 io.alu_op === ALU_OR,
//                 io.A | io.B,
//                 Mux(io.alu_op === ALU_XOR, io.A ^ io.B, Mux(io.alu_op === ALU_COPY_A, io.A, io.B))
//               )
//             )
//           )
//         )
//       )
//     )

//   io.out := out
//   io.sum := sum
// }
