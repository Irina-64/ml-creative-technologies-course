import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const build=path.join(root,'_build','slides');
const out=path.join(root,'labs','16','demo');
const skill='C:/Users/PC/.codex/plugins/cache/openai-primary-runtime/presentations/26.1025.11240/skills/presentations';
await fs.mkdir(build,{recursive:true}); await fs.mkdir(out,{recursive:true});
const source=await fs.readFile(path.join(out,'defense_slides.md'),'utf8');
const sections=source.split(/^# /m).filter(Boolean).map(x=>{const [title,...lines]=x.trim().split('\n');return {title:title.replace(/^\d+ /,''),body:lines.join('\n').trim()};});
const deck=Presentation.create({slideSize:{width:1280,height:720}});
deck.theme.defaultFont='Arial';
function text(slide,value,x,y,w,h,size=30,bold=false,color='#152A40') {
  const shape=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  shape.text=value; shape.text.style={typeface:'Arial',fontSize:size,color,bold,verticalAlignment:'top'};
  return shape;
}
for(const [i,section] of sections.entries()){
  const slide=deck.slides.add(); slide.background.fill='#FFFFFF';
  text(slide,section.title,70,65,1140,100,i===0?54:42,true);
  let body=section.body;
  if(i===4) {
    text(slide,'0,50',75,220,470,100,76,true,'#2563A6');
    text(slide,'TF-IDF baseline',75,330,470,55,30);
    text(slide,'1,00',690,220,470,100,76,true,'#147D64');
    text(slide,'Тот же TF-IDF со словарём',690,330,500,70,30);
    text(slide,'NDCG@3 на 12 validation-запросах. Меняется только нормализация слов.\nИскусственные шаблоны делают задачу простой; это не оценка реального архива.',75,455,1130,135,28);
  } else {
    text(slide,body,75,215,1120,350,32);
  }
  text(slide,`${i+1} / 8     Учебный пример ЛР 16`,75,650,1120,35,19,false,'#637082');
  if(slide.speakerNotes) slide.speakerNotes.text=section.body+'\nИсточник: материалы и фактические результаты репозитория Irina-64/ml-creative-technologies-course. Интервью и пользовательские сессии в образце симулированы.';
  try { const png=await deck.export({slide,format:'png',scale:1}); await fs.writeFile(path.join(build,`slide-${i+1}.png`),new Uint8Array(await png.arrayBuffer())); } catch(e){ console.log('Render fallback will use PowerPoint:',String(e).slice(0,180)); }
}
const candidate=path.join(build,'candidate.pptx');
await(await PresentationFile.exportPptx(deck)).save(candidate);
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools','artifact_tool_utils.mjs')).href);
await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:path.join(out,'Защита_демо.pptx'),pythonExecutable:'C:/Users/PC/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:path.join(skill,'container_tools','inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(skill,'container_tools','inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],explicitTotalSlideCount:8,fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(build,'validation.json')});
console.log('Created labs/16/demo/Защита_демо.pptx');
