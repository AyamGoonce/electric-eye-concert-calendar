(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.8156400e0e7fd15b.js","sha256":"8156400e0e7fd15b04adfe23fa0e4f9bfab0b514a4425b8c405861a26c9b46e8","count":2407,"publishedAt":"2026-09-10T23:16:30Z","state":"calendar-state.json","stateSha256":"8ad23237b290879acfe19b315214b60956b9a42ff318a39ad120dbe1ba45f46f"});
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
