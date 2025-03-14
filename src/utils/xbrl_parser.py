def parse_xbrl(instance_path: str, taxonomy_path: Optional[str] = None) -> Dict:
    """
    Parse XBRL instance file and taxonomy file.

    Args:
        instance_path: Path to XBRL instance file
        taxonomy_path: Path to taxonomy file (optional)

    Returns:
        Dictionary with parsed financial data
    """
    try:
        logger.info(f"Parsing XBRL file: {instance_path}")

        tree = ET.parse(instance_path)
        root = tree.getroot()

        # Extract namespaces
        namespaces = {k: v for k, v in root.attrib.items() 
                     if k.startswith('xmlns:')}

        # Extract facts (simplified approach)
        facts = extract_facts_from_xbrl(root)

        # Create structured report data
        report_data = {
            'facts': facts,
            'file_info': {
                'instance_filename': os.path.basename(instance_path),
                'taxonomy_filename': os.path.basename(taxonomy_path) if taxonomy_path else None,
                'file_size': os.path.getsize(instance_path)
            }
        }

        return report_data

    except Exception as e:
        logger.error(f"Error parsing XBRL: {str(e)}")
        return {}

def extract_facts_from_xbrl(root: ET.Element) -> Dict:
    """
    Extract facts from XBRL document root element.

    Args:
        root: Root element of XBRL document

    Returns:
        Dictionary of extracted facts
    """
    facts = {}
    for elem in root.iter():
        if not elem.attrib:
            continue

        # Get context reference and value
        context_ref = elem.attrib.get('contextRef')
        if context_ref and elem.text and elem.text.strip():
            tag_name = elem.tag.split('}')[-1]
            facts[f"{tag_name}_{context_ref}"] = {
                'value': elem.text.strip(),
                'context': context_ref,
                'name': tag_name
            }

    return facts