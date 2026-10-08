# 通道图环路清单（netlist_graph v1）

- 种子: `icache_io_cpu_resp_valid`, max_len=12
- 图例: 通道节点 `<实例>.<通道>.[fwd|bwd]`; 环边分层 wire(布线)/module:<模块>(模块内摘要)

共 137 条通道环。

## 环 1 (4 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 2 (8 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 3 (8 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 4 (8 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 5 (8 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 6 (8 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 7 (8 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 8 (8 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 9 (8 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 10 (8 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 11 (8 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 12 (9 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.ar.bwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `arb.icache.ar.bwd`: wire
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 13 (9 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.ar.bwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `arb.icache.ar.bwd`: wire
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 14 (9 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.ar.bwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `arb.icache.ar.bwd`: wire
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 15 (9 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.ar.bwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `arb.icache.ar.bwd`: wire
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 16 (9 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.ar.bwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `arb.icache.ar.bwd`: wire
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 17 (9 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.ar.bwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `arb.icache.ar.bwd`: wire
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 18 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 19 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 20 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 21 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 22 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 23 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 24 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 25 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 26 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 27 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 28 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 29 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 30 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 31 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 32 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 33 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 34 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 35 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 36 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 37 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 38 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.nasti.ar.fwd
  -> arb.icache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.nasti.ar.fwd`: module:AGICacheProp
- `icache.nasti.ar.fwd` -> `arb.icache.ar.fwd`: wire
- `arb.icache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 39 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 40 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 41 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 42 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 43 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 44 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 45 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 46 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 47 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 48 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 49 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 50 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 51 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 52 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 53 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 54 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 55 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 56 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 57 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 58 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 59 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 60 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 61 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 62 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 63 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 64 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 65 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 66 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 67 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 68 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 69 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 70 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 71 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 72 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 73 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 74 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 75 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 76 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 77 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 78 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 79 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 80 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 81 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 82 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 83 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 84 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 85 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 86 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 87 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 88 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 89 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 90 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 91 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 92 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 93 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 94 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 95 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 96 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 97 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 98 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 99 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 100 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 101 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.dcache.abort.fwd`: module:AGDatapathProp
- `dpath.dcache.abort.fwd` -> `dcache.cpu.abort.fwd`: wire
- `dcache.cpu.abort.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 102 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.nasti.ar.fwd
  -> arb.icache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.nasti.ar.fwd`: module:AGICacheProp
- `icache.nasti.ar.fwd` -> `arb.icache.ar.fwd`: wire
- `arb.icache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 103 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 104 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 105 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 106 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 107 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 108 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 109 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 110 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 111 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 112 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 113 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 114 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 115 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 116 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 117 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 118 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 119 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 120 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 121 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.aw.bwd
  -> dcache.nasti.aw.bwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.aw.bwd`: module:AGMemArbiterProp
- `arb.dcache.aw.bwd` -> `dcache.nasti.aw.bwd`: wire
- `dcache.nasti.aw.bwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 122 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 123 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 124 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 125 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.ar.bwd
  -> dcache.nasti.ar.bwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.ar.bwd`: module:AGMemArbiterProp
- `arb.dcache.ar.bwd` -> `dcache.nasti.ar.bwd`: wire
- `dcache.nasti.ar.bwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 126 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 127 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 128 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 129 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.b.fwd`: module:AGMemArbiterProp
- `arb.dcache.b.fwd` -> `dcache.nasti.b.fwd`: wire
- `dcache.nasti.b.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 130 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 131 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 132 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 133 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.r.fwd
  -> dcache.nasti.r.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.r.fwd`: module:AGMemArbiterProp
- `arb.dcache.r.fwd` -> `dcache.nasti.r.fwd`: wire
- `dcache.nasti.r.fwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 134 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.nasti.w.fwd`: module:AGICacheProp
- `dcache.nasti.w.fwd` -> `arb.dcache.w.fwd`: wire
- `arb.dcache.w.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 135 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.ar.bwd`: module:AGMemArbiterProp
- `arb.icache.ar.bwd` -> `icache.nasti.ar.bwd`: wire
- `icache.nasti.ar.bwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 136 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.nasti.ar.fwd`: module:AGICacheProp
- `dcache.nasti.ar.fwd` -> `arb.dcache.ar.fwd`: wire
- `arb.dcache.ar.fwd` -> `arb.icache.r.fwd`: module:AGMemArbiterProp
- `arb.icache.r.fwd` -> `icache.nasti.r.fwd`: wire
- `icache.nasti.r.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

## 环 137 (12 跳)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.w.bwd
  -> dcache.nasti.w.bwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
边分层:
- `icache.cpu.resp.fwd` -> `dpath.icache.resp.fwd`: wire
- `dpath.icache.resp.fwd` -> `dpath.dcache.req.fwd`: module:AGDatapathProp
- `dpath.dcache.req.fwd` -> `dcache.cpu.req.fwd`: wire
- `dcache.cpu.req.fwd` -> `dcache.nasti.aw.fwd`: module:AGICacheProp
- `dcache.nasti.aw.fwd` -> `arb.dcache.aw.fwd`: wire
- `arb.dcache.aw.fwd` -> `arb.dcache.w.bwd`: module:AGMemArbiterProp
- `arb.dcache.w.bwd` -> `dcache.nasti.w.bwd`: wire
- `dcache.nasti.w.bwd` -> `dcache.cpu.resp.fwd`: module:AGICacheProp
- `dcache.cpu.resp.fwd` -> `dpath.dcache.resp.fwd`: wire
- `dpath.dcache.resp.fwd` -> `dpath.icache.req.fwd`: module:AGDatapathProp
- `dpath.icache.req.fwd` -> `icache.cpu.req.fwd`: wire
- `icache.cpu.req.fwd` -> `icache.cpu.resp.fwd`: module:AGICacheProp

---
# 其它性质的敏感集与最短环测试

## F response (ICache 取指响应)

- 根信号: `icache_io_cpu_req_valid`, `icache_io_cpu_resp_valid`
- 敏感通道 32 个: `arb.dcache.ar.bwd`, `arb.dcache.ar.fwd`, `arb.dcache.aw.bwd`, `arb.dcache.aw.fwd`, `arb.dcache.b.fwd`, `arb.dcache.r.fwd`, `arb.dcache.w.bwd`, `arb.dcache.w.fwd`, `arb.icache.ar.bwd`, `arb.icache.ar.fwd`, `arb.icache.r.fwd`, `dcache.cpu.abort.fwd`, `dcache.cpu.req.fwd`, `dcache.cpu.resp.fwd`, `dcache.nasti.ar.bwd`, `dcache.nasti.ar.fwd`, `dcache.nasti.aw.bwd`, `dcache.nasti.aw.fwd`, `dcache.nasti.b.fwd`, `dcache.nasti.r.fwd`, `dcache.nasti.w.bwd`, `dcache.nasti.w.fwd`, `dpath.dcache.abort.fwd`, `dpath.dcache.req.fwd`, `dpath.dcache.resp.fwd`, `dpath.icache.req.fwd`, `dpath.icache.resp.fwd`, `icache.cpu.req.fwd`, `icache.cpu.resp.fwd`, `icache.nasti.ar.bwd`, `icache.nasti.ar.fwd`, `icache.nasti.r.fwd`
- 过种子最短环 50 条 (截前10):

  - (4) icache.cpu.req.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.icache.req.fwd -> icache.cpu.req.fwd
  - (8) icache.cpu.req.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.abort.fwd -> dcache.cpu.abort.fwd -> dcache.cpu.resp.fwd -> dpath.dcache.resp.fwd -> dpath.icache.req.fwd -> icache.cpu.req.fwd
  - (8) icache.cpu.req.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.req.fwd -> dcache.cpu.req.fwd -> dcache.cpu.resp.fwd -> dpath.dcache.resp.fwd -> dpath.icache.req.fwd -> icache.cpu.req.fwd
  - (8) icache.cpu.req.fwd -> icache.nasti.ar.fwd -> arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.cpu.resp.fwd -> dpath.dcache.resp.fwd -> dpath.icache.req.fwd -> icache.cpu.req.fwd
  - (12) icache.cpu.req.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.abort.fwd -> dcache.cpu.abort.fwd -> dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.cpu.resp.fwd -> dpath.dcache.resp.fwd -> dpath.icache.req.fwd -> icache.cpu.req.fwd
  - (12) icache.cpu.req.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.abort.fwd -> dcache.cpu.abort.fwd -> dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.ar.bwd -> dcache.nasti.ar.bwd -> dcache.cpu.resp.fwd -> dpath.dcache.resp.fwd -> dpath.icache.req.fwd -> icache.cpu.req.fwd
  - (12) icache.cpu.req.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.abort.fwd -> dcache.cpu.abort.fwd -> dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.b.fwd -> dcache.nasti.b.fwd -> dcache.cpu.resp.fwd -> dpath.dcache.resp.fwd -> dpath.icache.req.fwd -> icache.cpu.req.fwd
  - (12) icache.cpu.req.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.abort.fwd -> dcache.cpu.abort.fwd -> dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.r.fwd -> dcache.nasti.r.fwd -> dcache.cpu.resp.fwd -> dpath.dcache.resp.fwd -> dpath.icache.req.fwd -> icache.cpu.req.fwd
  - (12) icache.cpu.req.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.abort.fwd -> dcache.cpu.abort.fwd -> dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.w.bwd -> dcache.nasti.w.bwd -> dcache.cpu.resp.fwd -> dpath.dcache.resp.fwd -> dpath.icache.req.fwd -> icache.cpu.req.fwd
  - (12) icache.cpu.req.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.abort.fwd -> dcache.cpu.abort.fwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.cpu.resp.fwd -> dpath.dcache.resp.fwd -> dpath.icache.req.fwd -> icache.cpu.req.fwd

## F nastiReadReqReady (读请求公平)

- 根信号: `icache_io_nasti_ar_valid`, `icache_io_nasti_ar_ready`
- 敏感通道 32 个: `arb.dcache.ar.bwd`, `arb.dcache.ar.fwd`, `arb.dcache.aw.bwd`, `arb.dcache.aw.fwd`, `arb.dcache.b.fwd`, `arb.dcache.r.fwd`, `arb.dcache.w.bwd`, `arb.dcache.w.fwd`, `arb.icache.ar.bwd`, `arb.icache.ar.fwd`, `arb.icache.r.fwd`, `dcache.cpu.abort.fwd`, `dcache.cpu.req.fwd`, `dcache.cpu.resp.fwd`, `dcache.nasti.ar.bwd`, `dcache.nasti.ar.fwd`, `dcache.nasti.aw.bwd`, `dcache.nasti.aw.fwd`, `dcache.nasti.b.fwd`, `dcache.nasti.r.fwd`, `dcache.nasti.w.bwd`, `dcache.nasti.w.fwd`, `dpath.dcache.abort.fwd`, `dpath.dcache.req.fwd`, `dpath.dcache.resp.fwd`, `dpath.icache.req.fwd`, `dpath.icache.resp.fwd`, `icache.cpu.req.fwd`, `icache.cpu.resp.fwd`, `icache.nasti.ar.bwd`, `icache.nasti.ar.fwd`, `icache.nasti.r.fwd`
- 过种子最短环 50 条 (截前10):

  - (8) icache.nasti.ar.fwd -> arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.icache.ar.bwd -> icache.nasti.ar.bwd -> icache.nasti.ar.fwd
  - (8) icache.nasti.ar.fwd -> arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd -> icache.nasti.ar.fwd
  - (8) icache.nasti.ar.fwd -> arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd -> icache.nasti.ar.fwd
  - (8) icache.nasti.ar.fwd -> arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd -> icache.nasti.ar.fwd
  - (9) icache.nasti.ar.fwd -> arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.dcache.ar.bwd -> arb.icache.ar.bwd -> icache.nasti.ar.bwd -> icache.nasti.ar.fwd
  - (9) icache.nasti.ar.fwd -> arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.ar.bwd -> arb.icache.ar.bwd -> icache.nasti.ar.bwd -> icache.nasti.ar.fwd
  - (9) icache.nasti.ar.fwd -> arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.dcache.ar.bwd -> arb.icache.ar.bwd -> icache.nasti.ar.bwd -> icache.nasti.ar.fwd
  - (12) icache.nasti.ar.fwd -> arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.dcache.ar.bwd -> dcache.nasti.ar.bwd -> dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd -> icache.nasti.ar.fwd
  - (12) icache.nasti.ar.fwd -> arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.dcache.ar.bwd -> dcache.nasti.ar.bwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd -> icache.nasti.ar.fwd
  - (12) icache.nasti.ar.fwd -> arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.dcache.ar.bwd -> dcache.nasti.ar.bwd -> dcache.cpu.resp.fwd -> dpath.dcache.resp.fwd -> dpath.icache.req.fwd -> icache.cpu.req.fwd -> icache.nasti.ar.fwd

## nasti 读数据及时响应 X3

- 根信号: `icache_io_nasti_r_valid`, `icache_io_nasti_r_ready`, `icache_io_nasti_r_bits_last`
- 敏感通道 33 个: `arb.dcache.ar.bwd`, `arb.dcache.ar.fwd`, `arb.dcache.aw.bwd`, `arb.dcache.aw.fwd`, `arb.dcache.b.fwd`, `arb.dcache.r.fwd`, `arb.dcache.w.bwd`, `arb.dcache.w.fwd`, `arb.icache.ar.bwd`, `arb.icache.ar.fwd`, `arb.icache.r.fwd`, `dcache.cpu.abort.fwd`, `dcache.cpu.req.fwd`, `dcache.cpu.resp.fwd`, `dcache.nasti.ar.bwd`, `dcache.nasti.ar.fwd`, `dcache.nasti.aw.bwd`, `dcache.nasti.aw.fwd`, `dcache.nasti.b.fwd`, `dcache.nasti.r.fwd`, `dcache.nasti.w.bwd`, `dcache.nasti.w.fwd`, `dpath.dcache.abort.fwd`, `dpath.dcache.req.fwd`, `dpath.dcache.resp.fwd`, `dpath.icache.req.fwd`, `dpath.icache.resp.fwd`, `icache.cpu.req.fwd`, `icache.cpu.resp.fwd`, `icache.nasti.ar.bwd`, `icache.nasti.ar.fwd`, `icache.nasti.r.bwd`, `icache.nasti.r.fwd`
- 过种子最短环 50 条 (截前10):

  - (8) icache.nasti.r.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.abort.fwd -> dcache.cpu.abort.fwd -> dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd
  - (8) icache.nasti.r.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.abort.fwd -> dcache.cpu.abort.fwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd
  - (8) icache.nasti.r.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.abort.fwd -> dcache.cpu.abort.fwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd
  - (8) icache.nasti.r.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.icache.req.fwd -> icache.cpu.req.fwd -> icache.nasti.ar.fwd -> arb.icache.ar.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd
  - (12) icache.nasti.r.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.abort.fwd -> dcache.cpu.abort.fwd -> dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd
  - (12) icache.nasti.r.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.abort.fwd -> dcache.cpu.abort.fwd -> dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd
  - (12) icache.nasti.r.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.abort.fwd -> dcache.cpu.abort.fwd -> dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.ar.bwd -> dcache.nasti.ar.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd
  - (12) icache.nasti.r.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.abort.fwd -> dcache.cpu.abort.fwd -> dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.ar.bwd -> dcache.nasti.ar.bwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd
  - (12) icache.nasti.r.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.abort.fwd -> dcache.cpu.abort.fwd -> dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.b.fwd -> dcache.nasti.b.fwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd
  - (12) icache.nasti.r.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.abort.fwd -> dcache.cpu.abort.fwd -> dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.b.fwd -> dcache.nasti.b.fwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd

## DCache load 响应

- 根信号: `dcache_io_cpu_req_valid`, `dcache_io_cpu_resp_valid`
- 敏感通道 32 个: `arb.dcache.ar.bwd`, `arb.dcache.ar.fwd`, `arb.dcache.aw.bwd`, `arb.dcache.aw.fwd`, `arb.dcache.b.fwd`, `arb.dcache.r.fwd`, `arb.dcache.w.bwd`, `arb.dcache.w.fwd`, `arb.icache.ar.bwd`, `arb.icache.ar.fwd`, `arb.icache.r.fwd`, `dcache.cpu.abort.fwd`, `dcache.cpu.req.fwd`, `dcache.cpu.resp.fwd`, `dcache.nasti.ar.bwd`, `dcache.nasti.ar.fwd`, `dcache.nasti.aw.bwd`, `dcache.nasti.aw.fwd`, `dcache.nasti.b.fwd`, `dcache.nasti.r.fwd`, `dcache.nasti.w.bwd`, `dcache.nasti.w.fwd`, `dpath.dcache.abort.fwd`, `dpath.dcache.req.fwd`, `dpath.dcache.resp.fwd`, `dpath.icache.req.fwd`, `dpath.icache.resp.fwd`, `icache.cpu.req.fwd`, `icache.cpu.resp.fwd`, `icache.nasti.ar.bwd`, `icache.nasti.ar.fwd`, `icache.nasti.r.fwd`
- 过种子最短环 50 条 (截前10):

  - (8) dcache.cpu.req.fwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.cpu.resp.fwd -> dpath.dcache.resp.fwd -> dpath.dcache.req.fwd -> dcache.cpu.req.fwd
  - (8) dcache.cpu.req.fwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.dcache.ar.bwd -> dcache.nasti.ar.bwd -> dcache.cpu.resp.fwd -> dpath.dcache.resp.fwd -> dpath.dcache.req.fwd -> dcache.cpu.req.fwd
  - (8) dcache.cpu.req.fwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.dcache.b.fwd -> dcache.nasti.b.fwd -> dcache.cpu.resp.fwd -> dpath.dcache.resp.fwd -> dpath.dcache.req.fwd -> dcache.cpu.req.fwd
  - (8) dcache.cpu.req.fwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.req.fwd -> dcache.cpu.req.fwd
  - (8) dcache.cpu.req.fwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.dcache.r.fwd -> dcache.nasti.r.fwd -> dcache.cpu.resp.fwd -> dpath.dcache.resp.fwd -> dpath.dcache.req.fwd -> dcache.cpu.req.fwd
  - (9) dcache.cpu.req.fwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.dcache.ar.bwd -> arb.icache.ar.bwd -> icache.nasti.ar.bwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.req.fwd -> dcache.cpu.req.fwd
  - (12) dcache.cpu.req.fwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.icache.ar.bwd -> icache.nasti.ar.bwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.req.fwd -> dcache.cpu.req.fwd
  - (12) dcache.cpu.req.fwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.dcache.ar.bwd -> dcache.nasti.ar.bwd -> dcache.cpu.resp.fwd -> dpath.dcache.resp.fwd -> dpath.dcache.req.fwd -> dcache.cpu.req.fwd
  - (12) dcache.cpu.req.fwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.dcache.b.fwd -> dcache.nasti.b.fwd -> dcache.cpu.resp.fwd -> dpath.dcache.resp.fwd -> dpath.dcache.req.fwd -> dcache.cpu.req.fwd
  - (12) dcache.cpu.req.fwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.dcache.req.fwd -> dcache.cpu.req.fwd

## DCache 写回 (nasti.aw/w)

- 根信号: `dcache_io_nasti_aw_valid`, `dcache_io_nasti_w_valid`
- 敏感通道 32 个: `arb.dcache.ar.bwd`, `arb.dcache.ar.fwd`, `arb.dcache.aw.bwd`, `arb.dcache.aw.fwd`, `arb.dcache.b.fwd`, `arb.dcache.r.fwd`, `arb.dcache.w.bwd`, `arb.dcache.w.fwd`, `arb.icache.ar.bwd`, `arb.icache.ar.fwd`, `arb.icache.r.fwd`, `dcache.cpu.abort.fwd`, `dcache.cpu.req.fwd`, `dcache.cpu.resp.fwd`, `dcache.nasti.ar.bwd`, `dcache.nasti.ar.fwd`, `dcache.nasti.aw.bwd`, `dcache.nasti.aw.fwd`, `dcache.nasti.b.fwd`, `dcache.nasti.r.fwd`, `dcache.nasti.w.bwd`, `dcache.nasti.w.fwd`, `dpath.dcache.abort.fwd`, `dpath.dcache.req.fwd`, `dpath.dcache.resp.fwd`, `dpath.icache.req.fwd`, `dpath.icache.resp.fwd`, `icache.cpu.req.fwd`, `icache.cpu.resp.fwd`, `icache.nasti.ar.bwd`, `icache.nasti.ar.fwd`, `icache.nasti.r.fwd`
- 过种子最短环 52 条 (截前10):

  - (4) dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.aw.fwd
  - (4) dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.ar.bwd -> dcache.nasti.ar.bwd -> dcache.nasti.aw.fwd
  - (8) dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.dcache.ar.bwd -> dcache.nasti.ar.bwd -> dcache.nasti.aw.fwd
  - (8) dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.dcache.b.fwd -> dcache.nasti.b.fwd -> dcache.nasti.aw.fwd
  - (8) dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.dcache.r.fwd -> dcache.nasti.r.fwd -> dcache.nasti.aw.fwd
  - (8) dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.dcache.w.bwd -> dcache.nasti.w.bwd -> dcache.nasti.aw.fwd
  - (8) dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.ar.bwd -> dcache.nasti.ar.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.aw.fwd
  - (8) dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.ar.bwd -> dcache.nasti.ar.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.dcache.b.fwd -> dcache.nasti.b.fwd -> dcache.nasti.aw.fwd
  - (8) dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.ar.bwd -> dcache.nasti.ar.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.dcache.r.fwd -> dcache.nasti.r.fwd -> dcache.nasti.aw.fwd
  - (9) dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.ar.bwd -> arb.icache.ar.bwd -> icache.nasti.ar.bwd -> icache.nasti.ar.fwd -> arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.aw.fwd

## MemArbiter 仲裁公平

- 根信号: `arb_io_icache_ar_valid`, `arb_io_dcache_ar_valid`, `arb_io_nasti_ar_ready`
- 敏感通道 33 个: `arb.dcache.ar.bwd`, `arb.dcache.ar.fwd`, `arb.dcache.aw.bwd`, `arb.dcache.aw.fwd`, `arb.dcache.b.fwd`, `arb.dcache.r.fwd`, `arb.dcache.w.bwd`, `arb.dcache.w.fwd`, `arb.icache.ar.bwd`, `arb.icache.ar.fwd`, `arb.icache.r.fwd`, `arb.nasti.ar.bwd`, `dcache.cpu.abort.fwd`, `dcache.cpu.req.fwd`, `dcache.cpu.resp.fwd`, `dcache.nasti.ar.bwd`, `dcache.nasti.ar.fwd`, `dcache.nasti.aw.bwd`, `dcache.nasti.aw.fwd`, `dcache.nasti.b.fwd`, `dcache.nasti.r.fwd`, `dcache.nasti.w.bwd`, `dcache.nasti.w.fwd`, `dpath.dcache.abort.fwd`, `dpath.dcache.req.fwd`, `dpath.dcache.resp.fwd`, `dpath.icache.req.fwd`, `dpath.icache.resp.fwd`, `icache.cpu.req.fwd`, `icache.cpu.resp.fwd`, `icache.nasti.ar.bwd`, `icache.nasti.ar.fwd`, `icache.nasti.r.fwd`
- 过种子最短环 50 条 (截前10):

  - (8) arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.icache.ar.bwd -> icache.nasti.ar.bwd -> icache.nasti.ar.fwd -> arb.icache.ar.fwd
  - (8) arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd -> icache.nasti.ar.fwd -> arb.icache.ar.fwd
  - (8) arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd -> icache.nasti.ar.fwd -> arb.icache.ar.fwd
  - (8) arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd -> icache.nasti.ar.fwd -> arb.icache.ar.fwd
  - (9) arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.dcache.ar.bwd -> arb.icache.ar.bwd -> icache.nasti.ar.bwd -> icache.nasti.ar.fwd -> arb.icache.ar.fwd
  - (9) arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.dcache.ar.bwd -> arb.icache.ar.bwd -> icache.nasti.ar.bwd -> icache.nasti.ar.fwd -> arb.icache.ar.fwd
  - (9) arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.dcache.ar.bwd -> arb.icache.ar.bwd -> icache.nasti.ar.bwd -> icache.nasti.ar.fwd -> arb.icache.ar.fwd
  - (12) arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.icache.ar.bwd -> icache.nasti.ar.bwd -> icache.cpu.resp.fwd -> dpath.icache.resp.fwd -> dpath.icache.req.fwd -> icache.cpu.req.fwd -> icache.nasti.ar.fwd -> arb.icache.ar.fwd
  - (12) arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.dcache.ar.bwd -> dcache.nasti.ar.bwd -> dcache.nasti.aw.fwd -> arb.dcache.aw.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd -> icache.nasti.ar.fwd -> arb.icache.ar.fwd
  - (12) arb.icache.ar.fwd -> arb.dcache.aw.bwd -> dcache.nasti.aw.bwd -> dcache.nasti.ar.fwd -> arb.dcache.ar.fwd -> arb.dcache.ar.bwd -> dcache.nasti.ar.bwd -> dcache.nasti.w.fwd -> arb.dcache.w.fwd -> arb.icache.r.fwd -> icache.nasti.r.fwd -> icache.nasti.ar.fwd -> arb.icache.ar.fwd

---
# 环族分类（静态: 模块轨迹 × 回程通道）

137 条环 → **10 族**。每族: 代表环(最短) + 变化点(族内环之间不同的位置)。

## 族1（60 条）轨迹 icache → dpath → dcache → arb → dcache → arb → icache / 回程 (经 r.fwd 数据回)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.nasti.w.fwd
  -> arb.dcache.w.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
- 变化点[2] `dpath.dcache.abort.fwd` 可为: `dpath.dcache.req.fwd`
- 变化点[3] `dcache.cpu.abort.fwd` 可为: `dcache.cpu.req.fwd`
- 变化点[4] `dcache.nasti.aw.fwd` 可为: `dcache.nasti.ar.fwd`, `dcache.nasti.w.fwd`
- 变化点[5] `arb.dcache.aw.fwd` 可为: `arb.dcache.ar.fwd`, `arb.dcache.w.fwd`
- 变化点[6] `arb.dcache.b.fwd` 可为: `arb.dcache.ar.bwd`, `arb.dcache.aw.bwd`, `arb.dcache.r.fwd`, `arb.dcache.w.bwd`
- 变化点[7] `dcache.nasti.b.fwd` 可为: `dcache.nasti.ar.bwd`, `dcache.nasti.aw.bwd`, `dcache.nasti.r.fwd`, `dcache.nasti.w.bwd`
- 变化点[8] `dcache.nasti.w.fwd` 可为: `dcache.nasti.ar.fwd`, `dcache.nasti.aw.fwd`
- 变化点[9] `arb.dcache.w.fwd` 可为: `arb.dcache.ar.fwd`, `arb.dcache.aw.fwd`

## 族2（30 条）轨迹 icache → dpath → dcache → arb → dcache → dpath → icache / 回程 (经 r.fwd 数据回)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
- 变化点[2] `dpath.dcache.abort.fwd` 可为: `dpath.dcache.req.fwd`
- 变化点[3] `dcache.cpu.abort.fwd` 可为: `dcache.cpu.req.fwd`
- 变化点[4] `dcache.nasti.aw.fwd` 可为: `dcache.nasti.ar.fwd`, `dcache.nasti.w.fwd`
- 变化点[5] `arb.dcache.aw.fwd` 可为: `arb.dcache.ar.fwd`, `arb.dcache.w.fwd`
- 变化点[6] `arb.dcache.b.fwd` 可为: `arb.dcache.ar.bwd`, `arb.dcache.aw.bwd`, `arb.dcache.r.fwd`, `arb.dcache.w.bwd`
- 变化点[7] `dcache.nasti.b.fwd` 可为: `dcache.nasti.ar.bwd`, `dcache.nasti.aw.bwd`, `dcache.nasti.r.fwd`, `dcache.nasti.w.bwd`

## 族3（20 条）轨迹 icache → dpath → dcache → arb → dcache → arb → icache / 回程 icache.nasti.ar.bwd

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.dcache.b.fwd
  -> dcache.nasti.b.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
- 变化点[2] `dpath.dcache.abort.fwd` 可为: `dpath.dcache.req.fwd`
- 变化点[3] `dcache.cpu.abort.fwd` 可为: `dcache.cpu.req.fwd`
- 变化点[4] `dcache.nasti.aw.fwd` 可为: `dcache.nasti.w.fwd`
- 变化点[5] `arb.dcache.aw.fwd` 可为: `arb.dcache.w.fwd`
- 变化点[6] `arb.dcache.b.fwd` 可为: `arb.dcache.ar.bwd`, `arb.dcache.aw.bwd`, `arb.dcache.r.fwd`, `arb.dcache.w.bwd`
- 变化点[7] `dcache.nasti.b.fwd` 可为: `dcache.nasti.ar.bwd`, `dcache.nasti.aw.bwd`, `dcache.nasti.r.fwd`, `dcache.nasti.w.bwd`

## 族4（8 条）轨迹 icache → dpath → dcache → arb → icache / 回程 icache.nasti.ar.bwd

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
- 变化点[2] `dpath.dcache.abort.fwd` 可为: `dpath.dcache.req.fwd`
- 变化点[3] `dcache.cpu.abort.fwd` 可为: `dcache.cpu.req.fwd`
- 变化点[4] `dcache.nasti.ar.fwd` 可为: `dcache.nasti.aw.fwd`, `dcache.nasti.w.fwd`
- 变化点[5] `arb.dcache.ar.fwd` 可为: `arb.dcache.aw.fwd`, `arb.dcache.w.fwd`
- 变化点[6] `arb.icache.ar.bwd` 可为: `arb.dcache.ar.bwd`
- 变化点[7] `icache.nasti.ar.bwd` 可为: `arb.icache.ar.bwd`
- 变化点[8] `icache.cpu.resp.fwd` 可为: `icache.nasti.ar.bwd`

## 族5（6 条）轨迹 icache → dpath → dcache → arb → icache / 回程 (经 r.fwd 数据回)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.aw.fwd
  -> arb.dcache.aw.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
- 变化点[2] `dpath.dcache.abort.fwd` 可为: `dpath.dcache.req.fwd`
- 变化点[3] `dcache.cpu.abort.fwd` 可为: `dcache.cpu.req.fwd`
- 变化点[4] `dcache.nasti.aw.fwd` 可为: `dcache.nasti.ar.fwd`, `dcache.nasti.w.fwd`
- 变化点[5] `arb.dcache.aw.fwd` 可为: `arb.dcache.ar.fwd`, `arb.dcache.w.fwd`

## 族6（6 条）轨迹 icache → dpath → dcache → dpath → dcache → arb → icache / 回程 (经 r.fwd 数据回)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
- 变化点[2] `dpath.dcache.abort.fwd` 可为: `dpath.dcache.req.fwd`
- 变化点[3] `dcache.cpu.abort.fwd` 可为: `dcache.cpu.req.fwd`
- 变化点[6] `dpath.dcache.req.fwd` 可为: `dpath.dcache.abort.fwd`
- 变化点[7] `dcache.cpu.req.fwd` 可为: `dcache.cpu.abort.fwd`
- 变化点[8] `dcache.nasti.ar.fwd` 可为: `dcache.nasti.aw.fwd`, `dcache.nasti.w.fwd`
- 变化点[9] `arb.dcache.ar.fwd` 可为: `arb.dcache.aw.fwd`, `arb.dcache.w.fwd`

## 族7（2 条）轨迹 icache → dpath → dcache → dpath → icache / 回程 (经 r.fwd 数据回)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
- 变化点[2] `dpath.dcache.abort.fwd` 可为: `dpath.dcache.req.fwd`
- 变化点[3] `dcache.cpu.abort.fwd` 可为: `dcache.cpu.req.fwd`

## 族8（2 条）轨迹 icache → dpath → dcache → arb → icache → arb → icache / 回程 (经 r.fwd 数据回)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.nasti.ar.fwd
  -> arb.icache.ar.fwd
  -> arb.icache.r.fwd
  -> icache.nasti.r.fwd
  -> icache.cpu.resp.fwd
```
- 变化点[2] `dpath.dcache.abort.fwd` 可为: `dpath.dcache.req.fwd`
- 变化点[3] `dcache.cpu.abort.fwd` 可为: `dcache.cpu.req.fwd`

## 族9（2 条）轨迹 icache → dpath → dcache → dpath → dcache → arb → icache / 回程 icache.nasti.ar.bwd

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.dcache.abort.fwd
  -> dcache.cpu.abort.fwd
  -> dcache.cpu.resp.fwd
  -> dpath.dcache.resp.fwd
  -> dpath.dcache.req.fwd
  -> dcache.cpu.req.fwd
  -> dcache.nasti.ar.fwd
  -> arb.dcache.ar.fwd
  -> arb.icache.ar.bwd
  -> icache.nasti.ar.bwd
  -> icache.cpu.resp.fwd
```
- 变化点[2] `dpath.dcache.abort.fwd` 可为: `dpath.dcache.req.fwd`
- 变化点[3] `dcache.cpu.abort.fwd` 可为: `dcache.cpu.req.fwd`
- 变化点[6] `dpath.dcache.req.fwd` 可为: `dpath.dcache.abort.fwd`
- 变化点[7] `dcache.cpu.req.fwd` 可为: `dcache.cpu.abort.fwd`

## 族10（1 条）轨迹 icache → dpath → icache / 回程 (经 r.fwd 数据回)

```
icache.cpu.resp.fwd
  -> dpath.icache.resp.fwd
  -> dpath.icache.req.fwd
  -> icache.cpu.req.fwd
  -> icache.cpu.resp.fwd
```
