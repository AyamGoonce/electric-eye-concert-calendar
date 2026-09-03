(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.095aa0daf552238a.js","sha256":"095aa0daf552238a7641b984b411d20240850c271421b2467e20f405e7367672","count":2545,"publishedAt":"2026-09-03T16:39:20Z","state":"calendar-state.json","stateSha256":"5d87b1cc15c4ddb42d161dc080606cbbfdb96f85235a89923cd49c6ecaee388f"});
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
