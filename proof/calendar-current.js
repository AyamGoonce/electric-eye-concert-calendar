(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.8d10169ccb8696f2.js","sha256":"8d10169ccb8696f26264e4b91faa2948ef4c0be6b978a1c0435e94db4785bdae","count":2098,"publishedAt":"2026-11-28T13:27:31Z","state":"calendar-state.json","stateSha256":"ba7d67e52c5710ddff5b24114ca9db9f029d06699bda7e49b8047def23500568","sourceState":"calendar-source-state.json","sourceStateSha256":"fbc3042d1b45bf08d6bff63f35177b1857e5273789fcd6cc15e727e1c07c4520"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
