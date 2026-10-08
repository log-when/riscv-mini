ThisBuild / scalaVersion     := "2.13.10"
ThisBuild / version          := "2.5.0"
ThisBuild / organization     := "edu.berkeley.cs"

val chiselVersion = "3.7-SNAPSHOT"
val chiseltestVersion = "0.7-SNAPSHOT"

lazy val root = (project in file("."))
  .settings(
    name := "riscv-mini",
    libraryDependencies ++= Seq(
      "cn.ac.ios.tis" %% "chisel3" % chiselVersion,
      "cn.ac.ios.tis" %% "chiseltest" % chiseltestVersion % "test"
    ),
    scalacOptions ++= Seq(
      "-language:reflectiveCalls",
      "-deprecation",
      "-feature",
      "-Xcheckinit",
    ),
    addCompilerPlugin("cn.ac.ios.tis" % "chisel3-plugin" % chiselVersion cross CrossVersion.full),
    // addCompilerPlugin("edu.berkeley.cs" % "chisel3-plugin" % "3.6-SNAPSHOT" cross CrossVersion.full)
    // cn.ac.ios.tis:::chisel3-plugin:3.7-SNAPSHOT
  )
