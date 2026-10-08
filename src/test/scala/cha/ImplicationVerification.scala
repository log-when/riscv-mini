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

class ImplicationVerification extends Module {
  val io = IO(new Bundle {
    val a = Input(Bool())
    val b = Input(Bool())
    val c = Input(Bool())
    val d = Input(Bool())
    val e = Input(Bool())
    val f = Input(Bool())
    val g = Input(Bool())
    val h = Input(Bool())
    val i = Input(Bool())
    val j = Input(Bool())
    val k = Input(Bool())
    val l = Input(Bool())
    val m = Input(Bool())
    val n = Input(Bool())
  })

  val a = io.a
  val b = io.b
  val c = io.c
  val d = io.d
  val e = io.e
  val f = io.f
  val g = io.g
  val h = io.h
  val i = io.i
  val j = io.j
  val k = io.k
  val l = io.l
  val m = io.m
  val n = io.n

  chaAssume(this, "(G (f)) -> F G ((!(h | k)))")  // assume 1
  chaAssume(this, "(G ((j & h))) -> F G (k)")  // assume 2
  chaAssume(this, "(G (f)) -> F G (d)")  // assume 3
  chaAssume(this, "(G ((!d))) -> F G ((!f))")  // assume 4
  chaAssume(this, "(G ((j & h))) -> F G (n)")  // assume 5
  chaAssume(this, "(G ((!c))) -> F G ((!(j & h)))")  // assume 6
  chaAssume(this, "(G ((!f))) -> F G ((!(j & h)))")  // assume 7
  chaAssume(this, "(G (f)) -> F G ((h | k))")  // assume 8
  chaAssume(this, "(G (c)) -> F G ((!f))")  // assume 9
  chaAssume(this, "(G (i)) -> F G ((!f))")  // assume 10
  chaAssume(this, "(G ((!i))) -> F G ((!(j & h)))")  // assume 11
  chaAssume(this, "(G ((!h))) -> F G ((!f))")  // assume 12
  chaAssume(this, "(G ((j & h))) -> F G ((!d))")  // assume 13
  chaAssume(this, "(G (c)) -> F G ((!(j & h)))")  // assume 14
  chaAssume(this, "(G (f)) -> F G ((!f))")  // assume 15
  chaAssume(this, "(G (n)) -> F G ((!f))")  // assume 16
  chaAssume(this, "(G ((!d))) -> F G ((!c))")  // assume 17
  chaAssume(this, "(G (j)) -> F G ((!(j & h)))")  // assume 18
  chaAssume(this, "(G ((!(j & h)))) -> F G ((!f))")  // assume 19
  chaAssume(this, "(G ((j & h))) -> F G ((!c))")  // assume 20
  chaAssume(this, "(G (j)) -> F G ((!(h | k)))")  // assume 21
  chaAssume(this, "(G (d)) -> F G ((!(j & h)))")  // assume 22
  chaAssume(this, "(G ((!(h | k)))) -> F G ((!f))")  // assume 23
  chaAssume(this, "(G ((j & h))) -> F G ((!i))")  // assume 24
  chaAssume(this, "(G (f)) -> F G ((!c))")  // assume 25
  chaAssume(this, "(G (f)) -> F G (c)")  // assume 26
  chaAssume(this, "(G ((j & h))) -> F G (c)")  // assume 27
  chaAssume(this, "(G (f)) -> F G ((j & h))")  // assume 28
  chaAssume(this, "(G (k)) -> F G ((!j))")  // assume 29
  chaAssume(this, "(G (f)) -> F G ((!k))")  // assume 30
  chaAssume(this, "(G (f)) -> F G ((!i))")  // assume 31
  chaAssume(this, "(G (n)) -> F G ((!j))")  // assume 32
  chaAssume(this, "(G ((j & h))) -> F G (d)")  // assume 33
  chaAssume(this, "(G (c)) -> F G (d)")  // assume 34
  chaAssume(this, "(G ((j & h))) -> F G (i)")  // assume 35
  chaAssume(this, "(G ((j & h))) -> F G ((!(h | k)))")  // assume 36
  chaAssume(this, "(G (f)) -> F G ((!d))")  // assume 37
  chaAssume(this, "(G (j)) -> F G ((!c))")  // assume 38
  chaAssume(this, "(G (j)) -> F G ((!n))")  // assume 39
  chaAssume(this, "(G ((!i))) -> F G ((!f))")  // assume 40
  chaAssume(this, "(G ((!j))) -> F G ((!f))")  // assume 41
  chaAssume(this, "(G (j)) -> F G ((!d))")  // assume 42
  chaAssume(this, "(G ((j & h))) -> F G (f)")  // assume 43
  chaAssume(this, "(G (f)) -> F G (k)")  // assume 44
  chaAssume(this, "(G (c)) -> F G ((!i))")  // assume 45
  chaAssume(this, "(G (k)) -> F G ((!(j & h)))")  // assume 46
  chaAssume(this, "(G (n)) -> F G ((!(j & h)))")  // assume 47
  chaAssume(this, "(G (f)) -> F G ((!(j & h)))")  // assume 48
  chaAssume(this, "(G (i)) -> F G ((!c))")  // assume 49
  chaAssume(this, "(G (d)) -> F G ((!f))")  // assume 50
  chaAssume(this, "(G (f)) -> F G ((!j))")  // assume 51
  chaAssume(this, "(G (f)) -> F G ((!n))")  // assume 52
  chaAssume(this, "(G ((j & h))) -> F G ((!n))")  // assume 53
  chaAssume(this, "(G (k)) -> F G ((!f))")  // assume 54
  chaAssume(this, "(G (d)) -> F G ((!j))")  // assume 55
  chaAssume(this, "(G ((j & h))) -> F G ((!f))")  // assume 56
  chaAssume(this, "(G (j)) -> F G ((!f))")  // assume 57
  chaAssume(this, "(G (j)) -> F G ((!h))")  // assume 58
  chaAssume(this, "(G (j)) -> F G ((!k))")  // assume 59
  chaAssume(this, "(G (f)) -> F G (h)")  // assume 60
  chaAssume(this, "(G ((!c))) -> F G ((!f))")  // assume 61
  chaAssume(this, "(G (c)) -> F G ((!j))")  // assume 62
  chaAssume(this, "(G ((j & h))) -> F G ((!k))")  // assume 63
  chaAssume(this, "(G (f)) -> F G ((!h))")  // assume 64
  chaAssume(this, "(G ((!d))) -> F G ((!(j & h)))")  // assume 65
  chaAssume(this, "(G (i)) -> F G ((!(j & h)))")  // assume 66
  chaAssume(this, "(G (f)) -> F G (i)")  // assume 67
  chaAssume(this, "(G (f)) -> F G (n)")  // assume 68
  chaAssume(this, "(G (f)) -> F G (j)")  // assume 69
  chaAssume(this, "(G (b)) -> F G (m)")  // assume 70
  chaAssume(this, "(G ((!g))) -> F G ((!m))")  // assume 71
  chaAssume(this, "(G (b)) -> F G ((!e))")  // assume 72
  chaAssume(this, "(G ((!b))) -> F G ((!m))")  // assume 73
  chaAssume(this, "(G ((!l))) -> F G (((!a) | (!g)))")  // assume 74
  chaAssume(this, "(G (a)) -> F G ((!m))")  // assume 75
  chaAssume(this, "(G (((!a) | (!g)))) -> F G ((!m))")  // assume 76
  chaAssume(this, "(G (m)) -> F G ((!a))")  // assume 77
  chaAssume(this, "(G (a)) -> F G ((!b))")  // assume 78
  chaAssume(this, "(G (g)) -> F G ((!b))")  // assume 79
  chaAssume(this, "(G (m)) -> F G (((!a) | (!g)))")  // assume 80
  chaAssume(this, "(G (l)) -> F G ((!b))")  // assume 81
  chaAssume(this, "(G (m)) -> F G (a)")  // assume 82
  chaAssume(this, "(G (m)) -> F G (l)")  // assume 83
  chaAssume(this, "(G (e)) -> F G ((!m))")  // assume 84
  chaAssume(this, "(G (b)) -> F G ((!m))")  // assume 85
  chaAssume(this, "(G ((!g))) -> F G ((!b))")  // assume 86
  chaAssume(this, "(G (l)) -> F G ((!m))")  // assume 87
  chaAssume(this, "(G (e)) -> F G ((!b))")  // assume 88
  chaAssume(this, "(G ((!((!a) | (!g))))) -> F G ((!b))")  // assume 89
  chaAssume(this, "(G (b)) -> F G ((!l))")  // assume 90
  chaAssume(this, "(G ((!m))) -> F G ((!b))")  // assume 91
  chaAssume(this, "(G ((!((!a) | (!g))))) -> F G ((!m))")  // assume 92
  chaAssume(this, "(G (((!a) | (!g)))) -> F G ((!b))")  // assume 93
  chaAssume(this, "(G (m)) -> F G ((!l))")  // assume 94
  chaAssume(this, "(G (b)) -> F G ((!g))")  // assume 95
  chaAssume(this, "(G ((!l))) -> F G ((!m))")  // assume 96
  chaAssume(this, "(G (l)) -> F G ((!((!a) | (!g))))")  // assume 97
  chaAssume(this, "(G (b)) -> F G (g)")  // assume 98
  chaAssume(this, "(G (b)) -> F G (e)")  // assume 99
  chaAssume(this, "(G (m)) -> F G ((!b))")  // assume 100
  chaAssume(this, "(G ((!l))) -> F G ((!b))")  // assume 101
  chaAssume(this, "(G ((!a))) -> F G ((!b))")  // assume 102
  chaAssume(this, "(G (m)) -> F G (e)")  // assume 103
  chaAssume(this, "(G (l)) -> F G (g)")  // assume 104
  chaAssume(this, "(G (b)) -> F G ((!b))")  // assume 105
  chaAssume(this, "(G (g)) -> F G ((!m))")  // assume 106
  chaAssume(this, "(G ((!((!a) | (!g))))) -> F G (l)")  // assume 107
  chaAssume(this, "(G (b)) -> F G ((!((!a) | (!g))))")  // assume 108
  chaAssume(this, "(G (m)) -> F G ((!g))")  // assume 109
  chaAssume(this, "(G ((!e))) -> F G ((!m))")  // assume 110
  chaAssume(this, "(G ((!e))) -> F G ((!b))")  // assume 111
  chaAssume(this, "(G (b)) -> F G (a)")  // assume 112
  chaAssume(this, "(G (b)) -> F G (((!a) | (!g)))")  // assume 113
  chaAssume(this, "(G ((!a))) -> F G ((!m))")  // assume 114
  chaAssume(this, "(G ((!g))) -> F G ((!l))")  // assume 115
  chaAssume(this, "(G (m)) -> F G (b)")  // assume 116
  chaAssume(this, "(G ((!a))) -> F G ((!l))")  // assume 117
  chaAssume(this, "(G (l)) -> F G (a)")  // assume 118
  chaAssume(this, "(G (m)) -> F G (g)")  // assume 119
  chaAssume(this, "(G (b)) -> F G ((!a))")  // assume 120
  chaAssume(this, "(G (m)) -> F G ((!e))")  // assume 121
  chaAssume(this, "(G (((!a) | (!g)))) -> F G ((!l))")  // assume 122
  chaAssume(this, "(G (m)) -> F G ((!((!a) | (!g))))")  // assume 123
  chaAssume(this, "(G (m)) -> F G ((!m))")  // assume 124
  chaAssume(this, "(G (b)) -> F G (l)")  // assume 125
  chaAssume(this, "(G (k)) -> F G ((!g))")  // assume 126
  chaAssume(this, "(G (n)) -> F G ((!g))")  // assume 127
  chaAssume(this, "(G (k)) -> F G ((!n))")  // assume 128
  chaAssume(this, "(G (g)) -> F G ((!k))")  // assume 129
  chaAssume(this, "(G (g)) -> F G ((!n))")  // assume 130
  chaAssume(this, "(G (n)) -> F G ((!k))")  // assume 131
  chaAssume(this, "(G ((j & h))) -> F G ((!f))")  // assume 132
  // chaAssume(this, "(G (c)) -> F G (s1_gen_by7_in_ICacheProp)")  // assume 133
  chaAssume(this, "(G (f)) -> F G (l)")  // assume 134
  chaAssume(this, "(G (f)) -> F G ((!c))")  // assume 135
  chaAssume(this, "(G ((j & h))) -> F G ((!m))")  // assume 136
  chaAssume(this, "(G (c)) -> F G ((!(j & h)))")  // assume 137
  chaAssume(this, "(G (c)) -> F G ((j & h))")  // assume 138
  // chaAssume(this, "(G ((!s9_gen_by2_in_ICacheProp))) -> F G (b)")  // assume 139
  chaAssume(this, "(G (f)) -> F G ((!m))")  // assume 140
  chaAssume(this, "(G ((!l))) -> F G ((!f))")  // assume 141
  chaAssume(this, "(G (f)) -> F G ((!j))")  // assume 142
  chaAssume(this, "(G ((j & h))) -> F G (l)")  // assume 143
  chaAssume(this, "(G (c)) -> F G (j)")  // assume 144
  chaAssume(this, "(G (c)) -> F G (d)")  // assume 145
  chaAssume(this, "(G ((j & h))) -> F G (i)")  // assume 146
  chaAssume(this, "(G ((!l))) -> F G ((!(j & h)))")  // assume 147
  chaAssume(this, "(G (c)) -> F G ((!h))")  // assume 148
  chaAssume(this, "(G ((!j))) -> F G ((!c))")  // assume 149
  // chaAssume(this, "(G ((j & h))) -> F G (s9_gen_by2_in_ICacheProp)")  // assume 150
  chaAssume(this, "(G (f)) -> F G ((!a))")  // assume 151
  chaAssume(this, "(G (c)) -> F G ((!m))")  // assume 152
  chaAssume(this, "(G (c)) -> F G ((!d))")  // assume 153
  chaAssume(this, "(G ((!(j & h)))) -> F G ((!f))")  // assume 154
  chaAssume(this, "(G (c)) -> F G ((!f))")  // assume 155
  chaAssume(this, "(G (c)) -> F G (a)")  // assume 156
  chaAssume(this, "(G ((!d))) -> F G ((!c))")  // assume 157
  chaAssume(this, "(G (f)) -> F G ((!h))")  // assume 158
  chaAssume(this, "(G (f)) -> F G ((!b))")  // assume 159
  chaAssume(this, "(G (f)) -> F G ((!i))")  // assume 160
  chaAssume(this, "(G ((j & h))) -> F G (b)")  // assume 161
  chaAssume(this, "(G (h)) -> F G ((!c))")  // assume 162



  chaAssert(this, "G F a")  // assert
}

class ImplicationVerificationSpec extends AnyFlatSpec with ChiselScalatestTester with Formal {
  behavior of "Implication verification"
  it should "pass" in {
    verify(new ImplicationVerification, Seq(Ic3Check(20), RIC3EngineAnnotation))
  }
}
